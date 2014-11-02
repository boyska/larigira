import logging
log = logging.getLogger('mpdrandom')
import random

from mpd import MPDClient


def generate_by_artist(spec):
    '''choose HOWMANY random artists, and for each one choose a random song'''
    for attr in ('howmany',):
        if attr not in spec:
            raise ValueError("Malformed audiospec: missing '%s'" % attr)

    log.info('generating')
    c = MPDClient()
    c.connect('localhost', 6600)  # TODO: read global options somehow

    artists = c.list('artist')
    log.debug("got %d artists" % len(artists))
    if not artists:
        raise ValueError("no artists in your mpd database")
    for _ in xrange(spec['howmany']):
        artist = random.choice(artists)
        yield random.choice(c.find('artist', artist))['file']
