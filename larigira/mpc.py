from __future__ import print_function
import logging
import signal

import gevent
from gevent.queue import Queue
from mpd import MPDClient, ConnectionError, CommandError

from .event import Monitor
from .eventutils import ParentedLet, Timer
from .audiogen import audiogenerate


def get_mpd_client(conf):
    client = MPDClient(use_unicode=True)
    client.connect(conf['MPD_HOST'], conf['MPD_PORT'])

    return client


class MpcWatcher(ParentedLet):
    def __init__(self, queue, conf, client=None):
        ParentedLet.__init__(self, queue)
        self.log = logging.getLogger(self.__class__.__name__)
        self.conf = conf
        self.client = client  # assume it is already connected, or None

    def refresh_client(self):
        self.client = get_mpd_client(self.conf)

    def do_business(self):
        while True:
            try:
                if self.client is None:
                    self.refresh_client()

                self.log.info('idling')
                status = self.client.idle()[0]
            except ConnectionError:
                # TODO: should we emit an error just in case?
                self.client = None
                continue
            self.log.info(status)
            yield ('mpc', status)


class Player:
    def __init__(self, conf):
        self.conf = conf
        self.log = logging.getLogger(self.__class__.__name__)
        self.min_playlist_length = 10

    def _get_mpd(self):
        mpd_client = MPDClient(use_unicode=True)
        mpd_client.connect(self.conf['MPD_HOST'], self.conf['MPD_PORT'])
        return mpd_client

    def check_playlist(self):
        mpd_client = self._get_mpd()
        songs = mpd_client.playlist()
        current = mpd_client.currentsong()
        pos = int(current.get('pos', 0)) + 1
        if(len(songs) - pos >= self.min_playlist_length):
            return
        self.log.info('need to add new songs')
        picker = gevent.Greenlet(audiogenerate,
                                 self.conf['CONTINOUS_AUDIODESC'])

        def add(greenlet):
            uris = greenlet.value
            for uri in uris:
                assert type(uri) is str, type(uri)
                mpd_client.add(uri.strip())
        picker.link_value(add)
        picker.start()

    def enqueue(self, songs):
        mpd_client = self._get_mpd()
        assert type(songs) is dict
        assert 'uris' in songs
        spec = songs['audiospec']
        for uri in songs['uris']:
            assert type(uri) is str
            self.log.info('Adding {} to playlist (from {}={})'.
                          format(uri, songs['aid'], spec))
            insert_pos = 0 if len(mpd_client.playlistid()) == 0 else \
                int(mpd_client.currentsong().get('pos', 0)) + 1
            try:
                mpd_client.addid(uri, insert_pos)
            except CommandError:
                self.log.exception("Cannot insert song {}".format(uri))


class Controller(gevent.Greenlet):
    def __init__(self, conf):
        gevent.Greenlet.__init__(self)
        self.log = logging.getLogger(self.__class__.__name__)
        self.conf = conf
        self.q = Queue()
        self.player = Player(self.conf)
        if 'DB_URI' in self.conf:
            self.monitor = Monitor(self.q, self.conf)
            self.monitor.parent_greenlet = self
        else:
            self.monitor = None

    def _run(self):
        if self.monitor is not None:
            self.monitor.start()
        mw = MpcWatcher(self.q, self.conf, client=None)
        mw.parent_greenlet = self
        mw.start()
        t = Timer(int(self.conf['CHECK_SECS']) * 1000, self.q)
        t.parent_greenlet = self
        t.start()
        # at the very start, run a check!
        gevent.Greenlet.spawn(self.player.check_playlist)
        while True:
            value = self.q.get()
            self.log.debug('<- %s' % str(value))
            # emitter = value['emitter']
            kind = value['kind']
            args = value['args']
            if kind == 'timer' or (kind == 'mpc' and
                                   args[0] in ('player', 'playlist')):
                gevent.Greenlet.spawn(self.player.check_playlist)
            elif kind == 'mpc':
                pass
            elif kind == 'uris_enqueue':
                try:
                    self.player.enqueue(args[0])
                except AssertionError:
                    raise
                except Exception:
                    self.log.exception("Error while adding to queue; "
                                       "bad audiogen output?")
            elif (kind == 'signal' and args[0] == signal.SIGALRM) or \
                    kind == 'refresh':
                # it's a tick!
                self.log.debug("Reload")
                self.monitor.q.put(dict(kind='forcetick'))
                gevent.Greenlet.spawn(self.player.check_playlist)
            else:
                self.log.warning("Unknown message: %s" % str(value))
