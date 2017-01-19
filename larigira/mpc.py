from __future__ import print_function
import logging
import signal

import gevent
from gevent.queue import Queue
import mpd

from .event import Monitor
from .eventutils import ParentedLet, Timer
from .audiogen import audiogenerate
from .unused import UnusedCleaner


def get_mpd_client(conf):
    client = mpd.MPDClient(use_unicode=True)
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
        first_after_connection = True
        while True:
            try:
                if self.client is None:
                    self.refresh_client()
                if first_after_connection:
                    yield('mpc', 'connect')

                status = self.client.idle()[0]
            except (mpd.ConnectionError, ConnectionRefusedError,
                    FileNotFoundError) as exc:
                self.log.warning('Connection to MPD failed (%s: %s)',
                                 exc.__class__.__name__, exc)
                self.client = None
                first_after_connection = True
                gevent.sleep(5)
                continue
            else:
                first_after_connection = False
                yield ('mpc', status)


class Player:
    def __init__(self, conf):
        self.conf = conf
        self.log = logging.getLogger(self.__class__.__name__)
        self.min_playlist_length = 10
        self.tmpcleaner = UnusedCleaner(conf)
        self._continous_audiospec = self.conf['CONTINOUS_AUDIOSPEC']
        self.events_enabled = True

    def _get_mpd(self):
        mpd_client = mpd.MPDClient(use_unicode=True)
        try:
            mpd_client.connect(self.conf['MPD_HOST'], self.conf['MPD_PORT'])
        except (mpd.ConnectionError, ConnectionRefusedError,
                FileNotFoundError) as exc:
            self.log.warning('Connection to MPD failed (%s: %s)',
                             exc.__class__.__name__, exc)
            raise gevent.GreenletExit()
        return mpd_client

    @property
    def continous_audiospec(self):
        return self._continous_audiospec

    @continous_audiospec.setter
    def continous_audiospec(self, spec):
        self._continous_audiospec = self.conf['CONTINOUS_AUDIOSPEC'] \
                if spec is None else spec

        def clear_everything_but_current_song():
            mpdc = self._get_mpd()
            current = mpdc.currentsong()
            pos = int(current.get('pos', 0))
            for song in mpdc.playlistid():
                if int(song['pos']) != pos:
                    mpdc.deleteid(song['id'])

        gevent.Greenlet.spawn(clear_everything_but_current_song)

    def check_playlist(self):
        mpd_client = self._get_mpd()
        songs = mpd_client.playlist()
        current = mpd_client.currentsong()
        pos = int(current.get('pos', 0)) + 1
        if(len(songs) - pos >= self.min_playlist_length):
            return
        self.log.info('need to add new songs')
        picker = gevent.Greenlet(audiogenerate,
                                 self.continous_audiospec)

        def add(greenlet):
            uris = greenlet.value
            for uri in uris:
                assert type(uri) is str, type(uri)
                self.tmpcleaner.watch(uri.strip())
                mpd_client.add(uri.strip())
        picker.link_value(add)
        picker.start()

    def enqueue(self, songs):
        assert type(songs) is dict
        assert 'uris' in songs
        spec = [aspec.get('nick', aspec.eid) for aspec in songs['audiospecs']]
        if not self.events_enabled:
            self.log.debug('Ignoring <%s> (events disabled)',
                           ','.join(spec)
                           )
            return
        mpd_client = self._get_mpd()
        for uri in reversed(songs['uris']):
            assert type(uri) is str
            self.log.info('Adding %s to playlist (from <%s>:%s=%s)',
                          uri,
                          songs['timespec'].get('nick', ''),
                          songs['aids'], spec)
            insert_pos = 0 if len(mpd_client.playlistid()) == 0 else \
                int(mpd_client.currentsong().get('pos', 0)) + 1
            try:
                mpd_client.addid(uri, insert_pos)
            except mpd.CommandError:
                self.log.exception("Cannot insert song %s", uri)
            self.tmpcleaner.watch(uri.strip())


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
            self.log.debug('<- %s', str(value))
            # emitter = value['emitter']
            kind = value['kind']
            args = value['args']
            if kind == 'timer' or (kind == 'mpc' and
                                   args[0] in ('player', 'playlist',
                                               'connect')):
                gevent.Greenlet.spawn(self.player.check_playlist)
                try:
                    self.player.tmpcleaner.check_playlist()
                except:
                    pass
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
                self.log.warning("Unknown message: %s", str(value))
