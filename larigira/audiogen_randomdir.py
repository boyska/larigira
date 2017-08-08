import os
import logging
import shutil
import random
from tempfile import mkstemp
from pathlib import Path

from larigira.fsutils import scan_dir_audio, shortname, is_audio
log = logging.getLogger(__name__)


def candidates(paths):
    c = set()
    for path in paths:
        if not path.exists():
            log.warning("Can't find requested path: %s", path)
            continue
        if path.is_file() and is_audio(str(path)):
            c.add(str(path))
        elif path.is_dir():
            c.update(scan_dir_audio(str(path)))
    return c


def generate(spec):
    '''
    resolves audiospec-randomdir

    Recognized arguments:
        - paths [mandatory]    list of source paths
        - howmany [default=1]  number of audio files to pick
    '''
    spec.setdefault('howmany', 1)
    for attr in ('paths', ):
        if attr not in spec:
            raise ValueError("Malformed audiospec: missing '%s'" % attr)

    found_files = candidates([Path(p) for p in spec['paths']])

    picked = random.sample(found_files, int(spec['howmany']))

    # TODO: use specnick
    nick = spec.get('nick', spec.eid)
    for path in picked:
        tmp = mkstemp(suffix=os.path.splitext(path)[-1],
                      prefix='randomdir-%s-' % shortname(path))
        os.close(tmp[0])
        shutil.copy(path, tmp[1])
        log.info("copying %s -> %s", path, os.path.basename(tmp[1]))
        yield 'file://{}'.format(tmp[1])


generate.description = 'Picks random files from a specified directory'
