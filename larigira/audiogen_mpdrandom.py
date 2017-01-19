import logging
log = logging.getLogger('mpdrandom')
import random

from mpd import MPDClient

from .config import get_conf


def generate_by_artist(spec):
    '''choose HOWMANY random artists, and for each one choose a random song'''
    spec.setdefault('howmany', 1)
    log.info('generating')
    conf = get_conf()
    c = MPDClient(use_unicode=True)
    c.connect(conf['MPD_HOST'], conf['MPD_PORT'])

    artists = c.list('artist')
    log.debug("got %d artists", len(artists))
    if not artists:
        raise ValueError("no artists in your mpd database")
    for _ in range(spec['howmany']):
        artist = random.choice(artists)
        yield random.choice(c.find('artist', artist))['file']
