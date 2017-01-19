from __future__ import print_function
import logging
log = logging.getLogger('time-every')
from datetime import datetime, timedelta

from pytimeparse.timeparse import timeparse


def getdate(val):
    if type(val) is int:
        return datetime.fromtimestamp(val)
    return val


class Alarm(object):
    def __init__(self):
        pass

    def next_ring(self, current_time=None):
        '''if current_time is None, it is now()

        returns the next time it will ring; or None if it will not anymore
        '''
        raise NotImplementedError()

    def has_ring(self, time=None):
        '''returns True IFF the alarm will ring exactly at ``time``'''
        raise NotImplementedError()

    def all_rings(self, current_time=None):
        '''
        all future rings
        this, of course, is an iterator (they could be infinite)
        '''
        ring = self.next_ring(current_time)
        while ring is not None:
            yield ring
            ring = self.next_ring(ring)


class SingleAlarm(Alarm):
    '''
    rings a single time
    '''
    description = 'Only once, at a specified date and time'

    def __init__(self, obj):
        super().__init__()
        self.dt = getdate(obj['timestamp'])

    def next_ring(self, current_time=None):
        '''if current_time is None, it is now()'''
        if current_time is None:
            current_time = datetime.now()
        if current_time >= self.dt:
            return None
        return self.dt

    def has_ring(self, current_time=None):
        if current_time is None:
            current_time = datetime.now()
        return current_time == self.dt


class FrequencyAlarm(Alarm):
    '''
    rings on {t | exists a k integer >= 0 s.t. t = start+k*t, start<t<end}
    '''
    description = 'Events at a specified frequency. Example: every 30minutes'

    def __init__(self, obj):
        self.start = getdate(obj['start'])
        try:
            self.interval = int(obj['interval'])
        except ValueError:
            self.interval = timeparse(obj['interval'])
        assert type(self.interval) is int
        self.end = getdate(obj['end']) if 'end' in obj else None
        self.weekdays = [int(x) for x in obj['weekdays']] if \
            'weekdays' in obj else None
        if self.weekdays is not None:
            for weekday in self.weekdays:
                if not 1 <= weekday <= 7:
                    raise ValueError('Not a valid weekday: {}'
                                     .format(weekday))

    def next_ring(self, current_time=None):
        '''if current_time is None, it is now()'''
        if current_time is None:
            current_time = datetime.now()
        if self.end is not None and current_time > self.end:
            return None
        if current_time < self.start:
            return self.start
        if self.end is not None:
            assert self.start <= current_time <= self.end
        else:
            assert self.start <= current_time
        # this "infinite" loop is required by the weekday exclusion: in
        # fact, it is necessary to retry until a valid event/weekday is
        # found. a "while True" might have been more elegant (and maybe
        # fast), but this gives a clear upper bound to the cycle.
        for _ in range(60*60*24*7 // self.interval):
            n_interval = (
                (current_time - self.start).total_seconds() // self.interval
                ) + 1
            ring = self.start + timedelta(seconds=self.interval * n_interval)
            if ring == current_time:
                ring += timedelta(seconds=self.interval)
            if self.end is not None and ring > self.end:
                return None
            if self.weekdays is not None \
               and ring.isoweekday() not in self.weekdays:
                current_time = ring
                continue
            return ring
        log.warning("Can't find a valid time for event; "
                    "something went wrong")
        return None

    def has_ring(self, current_time=None):
        if current_time is None:
            current_time = datetime.now()
        if not self.start >= current_time >= self.end:
            return False

        n_interval = (current_time - self.start).total_seconds() // \
            self.interval
        expected_time = self.start + \
            timedelta(seconds=self.interval * n_interval)
        return expected_time == current_time

    def __str__(self):
        return 'FrequencyAlarm(every %ds)' % self.interval
