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
from event import Monitor

conf = {}
conf['CONTINOUS_AUDIODESC'] = dict(kind='mpd', howmany=1)
conf['MPD_HOST'] = os.getenv('MPD_HOST', 'localhost')
conf['MPD_PORT'] = int(os.getenv('MPD_PORT', '6600'))
conf['CACHING_TIME'] = 10


class MpcWatcher(ParentedLet):
    def __init__(self, queue, conf, client=None):
        ParentedLet.__init__(self, queue)
        self.log = logging.getLogger(self.__class__.__name__)
        self.conf = conf
        if client is None:
            self.client = MPDClient()
            # TODO: use config values
            self.client.connect(self.conf['MPD_HOST'], self.conf['MPD_PORT'])
        else:
            self.client = client  # assume it is already connected

    def do_business(self):
        while True:
            status = self.client.idle()[0]
            self.log.info(status)
            yield ('mpc', status)


class Player(gevent.Greenlet):
    def __init__(self, conf):
        gevent.Greenlet.__init__(self)
        self.min_playlist_length = 10
        self.log = logging.getLogger(self.__class__.__name__)
        self.q = Queue()
        self.conf = conf

    def _get_mpd(self):
        mpd_client = MPDClient()
        # TODO: use config values
        mpd_client.connect(self.conf['MPD_HOST'], self.conf['MPD_PORT'])
        return mpd_client

    def check_playlist(self):
        mpd_client = self._get_mpd()
        songs = mpd_client.playlist()
        if(len(songs) >= self.min_playlist_length):
            return
        self.log.info('need to add new songs')
        picker = gevent.Greenlet(audiogenerate,
                                 self.conf['CONTINOUS_AUDIODESC'])
        picker.link_value(lambda g: mpd_client.add(g.value[0].strip()))
        picker.start()

    def enqueue(self, songs):
        mpd_client = self._get_mpd()
        for song in songs:
            mpd_client.addid(song, 1)

    def _run(self):
        MpcWatcher(self.q, self.conf, client=None).start()
        Timer(60 * 1000, self.q).start()
        http_server = WSGIServer(('', 5000), rpc.create_app(self.q))
        http_server.start()
        while True:
            value = self.q.get()
            self.log.debug('<- %s' % str(value))
            # emitter = value['emitter']
            kind = value['kind']
            args = value['args']
            if kind == 'timer' or (kind == 'mpc' and args[0] == 'playlist'):
                gevent.Greenlet.spawn(self.check_playlist)
            elif kind == 'mpc':
                pass
            elif kind == 'add':
                self.enqueue(args[0])
            else:
                self.log.warning("Unknown message: %s" % str(value))


def on_player_crash(*args, **kwargs):
    print('A crash occurred in "main" greenlet. Aborting...')
    import sys
    sys.exit(1)


def main():
    # TODO: update conf from somewhere
    conf['DB_URI'] = 'larigira.db'
    p = Player(conf)
    p.start()
    # TODO: if <someoption> create Monitor(p.q)
    if 'DB_URI' in conf:
        m = Monitor(p.q, conf)
        m.start()
    p.link_exception(on_player_crash)

    def sig(*args):
        print('invoked sig', args)
        p.q.put('signal', *args)
    gevent.signal(signal.SIGHUP, sig, signal.SIGHUP)
    gevent.wait()

if __name__ == '__main__':
    main()
