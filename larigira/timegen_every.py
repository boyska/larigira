from __future__ import print_function
import logging
log = logging.getLogger('time-every')
from datetime import datetime, timedelta


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

    def __init__(self, obj):
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

    def __init__(self, obj):
        self.start = getdate(obj['start'])
        self.interval = obj['interval']
        self.end = getdate(obj['end']) if 'end' in obj else None

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
        n_interval = (
            (current_time - self.start).total_seconds() // self.interval
            ) + 1
        ring = self.start + timedelta(seconds=self.interval * n_interval)
        if ring == current_time:
            ring += timedelta(seconds=self.interval)
        if self.end is not None and ring > self.end:
            return None
        return ring

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
