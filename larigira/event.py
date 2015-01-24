from __future__ import print_function
from gevent import monkey
monkey.patch_all(subprocess=True)
import logging
FORMAT = '%(asctime)s|%(levelname)s[%(name)s:%(lineno)d] %(message)s'
logging.basicConfig(level=logging.INFO,
                    format=FORMAT,
                    datefmt='%H:%M:%S')
logging.getLogger('mpd').setLevel(logging.WARNING)
import signal
from datetime import datetime, timedelta

import gevent
from gevent.queue import Queue
from tinydb import TinyDB

from eventutils import ParentedLet
from timegen import timegenerate
from audiogen import audiogenerate


class EventModel(object):
    def __init__(self, uri):
        self.uri = uri
        self.db = TinyDB(uri)
        self.actions = self.db.table('actions')
        self.alarms = self.db.table('alarms')

    def get_action_by_id(self, action_id):
        return self.actions.get(eid=action_id)

    def get_alarm_by_id(self, alarm_id):
        return self.alarms.get(eid=alarm_id)

    def get_actions_by_alarm(self, alarm):
        for action_id in alarm.get('actions', []):
            yield self.get_action_by_id(action_id)

    def get_all_alarms(self):
        return self.alarms.all()

    def get_all_alarms_expanded(self):
        for alarm in self.get_all_alarms():
            for action in self.get_actions_by_alarm(alarm):
                yield alarm, action

    def add_event(self, alarm, actions):
        action_ids = [self.actions.insert(a) for a in actions]
        alarm['actions'] = action_ids
        return self.alarms.insert(alarm)


class EventSource(ParentedLet):
    def __init__(self, queue, uri):
        ParentedLet.__init__(self, queue)
        self.log = logging.getLogger(self.__class__.__name__)
        self.log.debug('uri is %s' % uri)
        self.model = EventModel(uri)
        self.log.debug('opened %s' % uri)

    def parent_msg(self, kind, *args):
        if kind == 'add':
            msg = ParentedLet.parent_msg(self, kind, *args[2:])
            msg['timespec'] = args[0]
            msg['audiospec'] = args[1]
        else:
            msg = ParentedLet.parent_msg(self, kind, *args)
        return msg

    def reload_id(self, alarm_id):
        '''
        Check if the event is still valid, and put "add" messages on queue
        '''
        alarm = self.model.get_alarm_by_id(alarm_id)
        for action in self.model.get_actions_by_alarm(alarm):
            self.send_to_parent('add', alarm, action)

    def do_business(self):
        for alarm, action in self.model.get_all_alarms_expanded():
            self.log.debug('scheduling {}'.format(alarm))
            yield ('add', alarm, action)


class Monitor(ParentedLet):
    def __init__(self, parent_queue, conf):
        ParentedLet.__init__(self, parent_queue)
        self.log = logging.getLogger(self.__class__.__name__)
        self.q = Queue()
        self.running = {}
        self.conf = conf
        self.source = EventSource(self.q, uri=conf['DB_URI'])

    def add(self, timespec, audiospec):
        '''
        this is somewhat recursive: after completion calls reload_id, which
        could call this method again
        '''
        now = datetime.now() + timedelta(seconds=self.conf['CACHING_TIME'])
        try:
            when = next(timegenerate(timespec, now=now))
        except:
            logging.exception("Could not generate "
                              "an alarm from timespec {}".format(timespec))
        delta = when - now
        assert delta.total_seconds() > 0
        self.log.info('Will run after %d seconds' % delta.total_seconds())

        audiogen = gevent.spawn_later(delta.total_seconds(), audiogenerate,
                                      audiospec)
        self.running[timespec.eid] = audiogen
        gevent.spawn_later(delta.total_seconds(),
                           self.source.reload_id,
                           timespec.eid)
        # FIXME: audiogen is ready in a moment between
        # exact_time - CACHING_TIME and the exact_time
        # atm we are just ignoring this "window", saying that any moment is
        # fine
        # the more correct thing will be to wait till that exact moment
        # adding another spawn_later
        audiogen.link_value(lambda g: self.log.info(
            'should play %s' % str(g.value)))
        audiogen.link_exception(lambda g: self.log.exception(
            'Failure in audiogen {}'.format(audiospec)))
        audiogen.link_value(lambda g: self.send_to_parent('add', g.value))

    def _run(self):
        self.source.start()
        while True:
            value = self.q.get()
            self.log.debug('<- %s' % str(value))
            kind = value['kind']
            if kind == 'add':
                self.add(value['timespec'], value['audiospec'])
            elif kind == 'remove':
                raise NotImplementedError()
            else:
                self.log.warning("Unknown message: %s" % str(value))


def on_player_crash(*args, **kwargs):
    print('A crash occurred in "main" greenlet. Aborting...')
    import sys
    sys.exit(1)


def main():
    conf = dict(CACHING_TIME=10, DB_URI='larigira.db')
    monitor = Monitor(Queue(), conf)
    monitor.start()
    monitor.link_exception(on_player_crash)

    def sig(*args):
        print('invoked sig', args)
        monitor.q.put('signal', *args)
    gevent.signal(signal.SIGHUP, sig, signal.SIGHUP)
    gevent.wait()

if __name__ == '__main__':
    main()
