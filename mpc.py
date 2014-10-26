from __future__ import print_function
from gevent import monkey
monkey.patch_all(subprocess=True)

import logging
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s %(message)s',
                    datefmt='%H:%M:%S')
from subprocess import check_output

import gevent
from gevent.queue import Queue


from eventutils import ParentedLet, CeleryTask, Timer
from task import create as create_continous


class MpcWatcher(ParentedLet):
    def __init__(self, queue):
        ParentedLet.__init__(self, queue)

    def do_business(self):
        while True:
            status = check_output(['mpc', 'idle']).decode('utf-8').strip()
            yield ('mpc', status)


class Player(gevent.Greenlet):
    def __init__(self):
        gevent.Greenlet.__init__(self)
        self.min_playlist_length = 10
        self.q = Queue()

    def check_playlist(self):
        out = check_output(['mpc', 'playlist']).decode('utf-8').strip()
        songs = out.split('\n')
        if(len(songs) >= self.min_playlist_length):

            return
        logging.info('need to add new songs')
        CeleryTask(create_continous, self.q).start()
        CeleryTask(create_continous, self.q).start()

    def _run(self):
        MpcWatcher(self.q).start()
        Timer(6000, self.q).start()
        while True:
            value = self.q.get()
            # emitter = value['emitter']
            kind = value['kind']
            args = value['args']
            if kind == 'timer':
                logging.info('CLOCK')
            if kind == 'timer' or (kind == 'mpc' and args[0] == 'playlist'):
                gevent.Greenlet.spawn(self.check_playlist)
            elif kind == 'celery':
                logging.info("celery: %s" % str(args))
            else:
                logging.warning("Unknown message: %s" % str(value))
            logging.info(str(value))


if __name__ == '__main__':
    p = Player()
    p.start()
    gevent.wait()
