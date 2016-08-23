from __future__ import print_function
import logging

import gevent
from gevent.queue import Queue
from mpd import MPDClient, ConnectionError, CommandError

from eventutils import ParentedLet, Timer
from audiogen import audiogenerate


def get_mpd_client(conf):
    client = MPDClient()
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


class Player(gevent.Greenlet):
    def __init__(self, conf):
        gevent.Greenlet.__init__(self)
        self.min_playlist_length = 10
        self.log = logging.getLogger(self.__class__.__name__)
        self.q = Queue()
        self.conf = conf

    def _get_mpd(self):
        mpd_client = MPDClient()
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
        picker.link_value(lambda g: mpd_client.add(g.value[0].strip()))
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

    def _run(self):
        mw = MpcWatcher(self.q, self.conf, client=None)
        mw.parent_greenlet = self
        mw.start()
        t = Timer(int(self.conf['CHECK_SECS']) * 1000, self.q)
        t.parent_greenlet = self
        t.start()
        # at the very start, run a check!
        gevent.Greenlet.spawn(self.check_playlist)
        while True:
            value = self.q.get()
            self.log.debug('<- %s' % str(value))
            # emitter = value['emitter']
            kind = value['kind']
            args = value['args']
            if kind == 'timer' or (kind == 'mpc' and args[0] in ('player', 'playlist')):
                gevent.Greenlet.spawn(self.check_playlist)
            elif kind == 'mpc':
                pass
            elif kind == 'add':
                self.enqueue(args[0])
            else:
                self.log.warning("Unknown message: %s" % str(value))
