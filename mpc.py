from __future__ import print_function
from gevent import monkey
monkey.patch_all(subprocess=True)

import logging
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s %(message)s',
                    datefmt='%H:%M:%S')
import signal

import gevent
from gevent.queue import Queue
from gevent.wsgi import WSGIServer
from mpd import MPDClient

from eventutils import ParentedLet, CeleryTask, Timer
from task import create as create_continous
import rpc


class MpcWatcher(ParentedLet):
    def __init__(self, queue, client=None):
        ParentedLet.__init__(self, queue)
        if client is None:
            self.client = MPDClient()
            # TODO: use config values
            self.client.connect("localhost", 6600)
        else:
            self.client = client  # assume it is already connected

    def do_business(self):
        while True:
            # status = check_output(['mpc', 'idle']).decode('utf-8').strip()
            status = self.client.idle()[0]
            logging.info(status)
            yield ('mpc', status)


class Player(gevent.Greenlet):
    def __init__(self):
        gevent.Greenlet.__init__(self)
        self.min_playlist_length = 10
        self.q = Queue()

    def check_playlist(self):
        mpd_client = MPDClient()
        # TODO: use config values
        mpd_client.connect("localhost", 6600)
        songs = mpd_client.playlist()
        if(len(songs) >= self.min_playlist_length):
            return
        logging.info('need to add new songs')
        CeleryTask(create_continous, self.q).start()
        CeleryTask(create_continous, self.q).start()

    def _run(self):
        MpcWatcher(self.q, client=None).start()
        Timer(6000, self.q).start()
        http_server = WSGIServer(('', 5000), rpc.create_app(self.q))
        http_server.start()
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


def on_player_crash(*args, **kwargs):
    print('A crash occurred in "main" greenlet. Aborting...')
    import sys
    sys.exit(1)


if __name__ == '__main__':
    p = Player()
    p.start()
    p.link_exception(on_player_crash)

    def sig(*args):
        print('invoked sig', args)
        p.q.put('signal', *args)
    gevent.signal(signal.SIGHUP, sig, signal.SIGHUP)
    gevent.wait()
