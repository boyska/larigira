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

from eventutils import ParentedLet
from timegen import timegenerate
from audiogen import audiogenerate


class EventSource(ParentedLet):
    def __init__(self, queue, uri):
        ParentedLet.__init__(self, queue)
        import pyejdb
        self.log = logging.getLogger(self.__class__.__name__)
        self.log.debug('uri is %s' % uri)
        self.ejdb = pyejdb.EJDB(uri,
                                pyejdb.JBOREADER | pyejdb.JBOLCKNB |
                                pyejdb.JBOTRUNC)
        self.log.debug('opened %s' % uri)

    def parent_msg(self, kind, *args):
        if kind == 'add':
            msg = ParentedLet.parent_msg(self, kind, *args[2:])
            msg['timespec'] = args[0]
            msg['audiospec'] = args[1]
        else:
            msg = ParentedLet.parent_msg(self, kind, *args)
        return msg

    def _get_actions_by_alarm(self, alarm):
        if 'actions' not in alarm:
            return
        for action_id in alarm['actions']:
            with self.ejdb.find('actions',
                                {'_id': action_id}) as subcur:
                for action in subcur:
                    yield action

    def _get_by_alarmid(self, alarmid):
        with self.ejdb.find('alarms', {'_id': alarmid}) as cur:
            if len(cur) > 1:
                self.log.warn("Found more than one alarm with given id")
            for alarm in cur:
                for action in self._get_actions_by_alarm(alarm):
                    yield alarm, action

    def reload(self):
        with self.ejdb.find('alarms', {}) as cur:
            for alarm in cur:
                self.log.info('%s\t%s' % (alarm['kind'],
                                          ', '.join(alarm.keys())))
                for action in self._get_actions_by_alarm(alarm):
                    yield alarm, action

    def reload_id(self, event_id):
        '''
        Check if the event is still valid, and put "add" messages on queue
        '''
        for alarm, action in self._get_by_alarmid(event_id):
            self.send_to_parent('add', alarm, action)

    def do_business(self):
        for alarm, action in self.reload():
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
        when = next(timegenerate(timespec, now=now))
        delta = when - now
        assert delta.total_seconds() > 0
        self.log.info('Will run after %d seconds' % delta.total_seconds())

        audiogen = gevent.spawn_later(delta.total_seconds(), audiogenerate,
                                      audiospec)
        self.running[timespec['_id']] = audiogen
        gevent.spawn_later(delta.total_seconds(),
                           self.source.reload_id,
                           timespec['_id'])
        # FIXME: audiogen is ready in a moment between
        # exact_time - CACHING_TIME and the exact_time
        # atm we are just ignoring this "window", saying that any moment is
        # fine
        # the more correct thing will be to wait till that exact moment
        # adding another spawn_later
        audiogen.link(lambda g: self.log.info('should play %s' % str(g.value)))
        audiogen.link(lambda g: self.send_to_parent('add', g.value))

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
