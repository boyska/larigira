from __future__ import print_function
from gevent import monkey
monkey.patch_all(subprocess=True)
import os

import logging
FORMAT = '%(asctime)s|%(levelname)s[%(name)s:%(lineno)d] %(message)s'
logging.basicConfig(level=logging.INFO,
                    format=FORMAT,
                    datefmt='%H:%M:%S')
import signal

import gevent
from gevent.queue import Queue
from gevent.wsgi import WSGIServer
from mpd import MPDClient

from eventutils import ParentedLet, Timer
import rpc
from audiogen import audiogenerate

CONTINOUS_AUDIODESC = dict(kind='mpd', howmany=1)
MPD_HOST = os.getenv('MPD_HOST', 'localhost')
MPD_PORT = int(os.getenv('MPD_PORT', '6600'))


class MpcWatcher(ParentedLet):
    def __init__(self, queue, client=None):
        ParentedLet.__init__(self, queue)
        self.log = logging.getLogger(self.__class__.__name__)
        if client is None:
            self.client = MPDClient()
            # TODO: use config values
            self.client.connect(MPD_HOST, MPD_PORT)
        else:
            self.client = client  # assume it is already connected

    def do_business(self):
        while True:
            status = self.client.idle()[0]
            self.log.info(status)
            yield ('mpc', status)


class Player(gevent.Greenlet):
    def __init__(self):
        gevent.Greenlet.__init__(self)
        self.min_playlist_length = 10
        self.log = logging.getLogger(self.__class__.__name__)
        self.q = Queue()

    def check_playlist(self):
        mpd_client = MPDClient()
        # TODO: use config values
        mpd_client.connect("localhost", 6600)
        songs = mpd_client.playlist()
        if(len(songs) >= self.min_playlist_length):
            return
        self.log.info('need to add new songs')
        picker = gevent.Greenlet(audiogenerate, CONTINOUS_AUDIODESC)
        picker.link_value(lambda g: mpd_client.add(g.value[0].strip()))
        picker.start()

    def _run(self):
        MpcWatcher(self.q, client=None).start()
        Timer(60 * 1000, self.q).start()
        http_server = WSGIServer(('', 5000), rpc.create_app(self.q))
        http_server.start()
        while True:
            value = self.q.get()
            self.log.debug('<- %s' % str(value))
            # emitter = value['emitter']
            kind = value['kind']
            args = value['args']
            if kind == 'timer':
                self.log.info('CLOCK')
            if kind == 'timer' or (kind == 'mpc' and args[0] == 'playlist'):
                gevent.Greenlet.spawn(self.check_playlist)
            else:
                self.log.warning("Unknown message: %s" % str(value))


def on_player_crash(*args, **kwargs):
    print('A crash occurred in "main" greenlet. Aborting...')
    import sys
    sys.exit(1)


def main():
    p = Player()
    p.start()
    p.link_exception(on_player_crash)

    def sig(*args):
        print('invoked sig', args)
        p.q.put('signal', *args)
    gevent.signal(signal.SIGHUP, sig, signal.SIGHUP)
    gevent.wait()

if __name__ == '__main__':
    main()
