from __future__ import print_function
from gevent import monkey
monkey.patch_all(subprocess=True)
import logging
logging.getLogger('mpd').setLevel(logging.WARNING)
from datetime import datetime, timedelta

import gevent
from gevent.queue import Queue
from tinydb import TinyDB

from .eventutils import ParentedLet, Timer
from .timegen import timegenerate
from .audiogen import audiogenerate


class EventModel(object):
    def __init__(self, uri):
        self.uri = uri
        self.db = None
        self.reload()

    def reload(self):
        if self.db is not None:
            self.db.close()
        self.db = TinyDB(self.uri, indent=2)
        self.actions = self.db.table('actions')
        self.alarms = self.db.table('alarms')

    def get_action_by_id(self, action_id):
        return self.actions.get(eid=action_id)

    def get_alarm_by_id(self, alarm_id):
        return self.alarms.get(eid=alarm_id)

    def get_actions_by_alarm(self, alarm):
        for action_id in alarm.get('actions', []):
            action = self.get_action_by_id(action_id)
            if action is None: continue
            yield action

    def get_all_alarms(self):
        return self.alarms.all()

    def get_all_actions(self):
        return self.actions.all()

    def get_all_alarms_expanded(self):
        for alarm in self.get_all_alarms():
            for action in self.get_actions_by_alarm(alarm):
                yield alarm, action

    def add_event(self, alarm, actions):
        action_ids = [self.add_action(a) for a in actions]
        alarm['actions'] = action_ids
        return self.alarms.insert(alarm)

    def add_action(self, action):
        return self.actions.insert(action)

    def add_alarm(self, alarm):
        return self.add_event(alarm, [])

    def update_alarm(self, alarmid, new_fields={}):
        return self.alarms.update(new_fields, eids=[alarmid])

    def update_action(self, actionid, new_fields={}):
        return self.actions.update(new_fields, eids=[actionid])

    def delete_alarm(self, alarmid):
        return self.alarms.remove(eids=[alarmid])

    def delete_action(self, actionid):
        return self.actions.remove(eids=[actionid])


class Monitor(ParentedLet):
    '''
    Manages timegenerators and audiogenerators.
    
    The mechanism is partially based on ticks, partially on scheduled actions.
    Ticks are emitted periodically; at every tick, :func:`on_tick
    <larigira.event.Monitor.on_tick>` checks if any event is "near enough". If
    an event is near enough, it is ":func:`scheduled
    <larigira.event.Monitor.schedule>`": a greenlet is run which will wait for
    the right time, then generate the audio, then submit to Controller.

    The tick mechanism allows for events to be changed on disk: if everything
    was scheduled immediately, no further changes would be possible.
    The scheduling mechanism allows for more precision, catching exactly the
    right time. Being accurate only with ticks would have required very
    frequent ticks, which is cpu-intensive.
    '''
    def __init__(self, parent_queue, conf):
        ParentedLet.__init__(self, parent_queue)
        self.log = logging.getLogger(self.__class__.__name__)
        self.running = {}
        self.conf = conf
        self.q = Queue()
        self.model = EventModel(self.conf['DB_URI'])
        self.ticker = Timer(int(self.conf['EVENT_TICK_SECS']) * 1000, self.q)

    def _alarm_missing_time(self, timespec):
        now = datetime.now() + timedelta(seconds=self.conf['CACHING_TIME'])
        try:
            when = next(timegenerate(timespec, now=now))
        except:
            logging.exception("Could not generate "
                              "an alarm from timespec %s", timespec)
        if when is None:
            # expired
            return None
        delta = (when - now).total_seconds()
        assert delta > 0
        return delta

    def on_tick(self):
        '''
        this is called every EVENT_TICK_SECS.
        Checks every event in the DB (which might be slightly CPU-intensive, so
        it is advisable to run it in its own greenlet); if the event is "near
        enough", schedule it; if it is too far, or already expired, ignore it.
        '''
        self.model.reload()
        for alarm in self.model.get_all_alarms():
            actions = list(self.model.get_actions_by_alarm(alarm))
            if alarm.eid in self.running:
                continue
            delta = self._alarm_missing_time(alarm)
            # why this 2*EVENT_TICK_SECS? EVENT_TICK_SECS would be enough,
            # but it is "tricky"; any small delay would cause the event to be
            # missed
            if delta is None:
                self.log.debug('Skipping event %s: will never ring',
                               alarm.get('nick', alarm.eid))
            elif delta <= 2*self.conf['EVENT_TICK_SECS']:
                self.log.debug('Scheduling event %s (%ds) => %s',
                               alarm.get('nick', alarm.eid),
                               delta,
                               [a.get('nick', a.eid) for a in actions]
                               )
                self.schedule(alarm, actions, delta)
            else:
                self.log.debug('Skipping event %s too far (%ds)',
                               alarm.get('nick', alarm.eid),
                               delta,
                               )

    def schedule(self, timespec, audiospecs, delta=None):
        '''
        prepare an event to be run at a specified time with the specified
        actions; the DB won't be read anymore after this call.

        This means that this call should not be done too early, or any update
        to the DB will be ignored.
        '''
        if delta is None:
            delta = self._alarm_missing_time(timespec)

        audiogen = gevent.spawn_later(delta,
                                      self.process_action,
                                      timespec, audiospecs)
        audiogen.parent_greenlet = self
        audiogen.doc = 'Will wait {} seconds, then generate audio "{}"'.format(
            delta,
            ','.join(aspec.get('nick', '') for aspec in audiospecs),
        )
        self.running[timespec.eid] = {
            'greenlet': audiogen,
            'running_time': datetime.now() + timedelta(seconds=delta),
            'timespec': timespec,
            'audiospecs': audiospecs
        }

    def process_action(self, timespec, audiospecs):
        '''Generate audio and submit it to Controller'''
        if timespec.eid in self.running:
            del self.running[timespec.eid]
        else:
            self.log.warning('Timespec %s completed but not in running '
                             'registry; this is most likely a bug',
                             timespec.get('nick', timespec.eid))
        uris = []
        for audiospec in audiospecs:
            try:
                uris.extend(audiogenerate(audiospec))
            except:
                self.log.error('audiogenerate for %s failed',
                               str(audiospec))
        self.send_to_parent('uris_enqueue',
                            dict(uris=uris,
                                 timespec=timespec,
                                 audiospecs=audiospecs,
                                 aids=[a.eid for a in audiospecs]))

    def _run(self):
        self.ticker.start()
        gevent.spawn(self.on_tick)
        while True:
            value = self.q.get()
            kind = value['kind']
            if kind in ('forcetick', 'timer'):
                gevent.spawn(self.on_tick)
            else:
                self.log.warning("Unknown message: %s", str(value))
