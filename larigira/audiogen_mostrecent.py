import os
import logging
import shutil
import time
from tempfile import mkstemp

from pytimeparse.timeparse import timeparse

from larigira.fsutils import scan_dir, shortname
log = logging.getLogger(__name__)


def get_mtime(fname):
    return int(os.path.getmtime(fname))


def recent_choose(paths, howmany, minepoch):
    found_files = {}
    for path in paths:
        if not os.path.exists(path):
            log.warning("Can't find requested path: %s", path)
            continue
        if os.path.isfile(path):
            found_files[path] = get_mtime(path)
        elif os.path.isdir(path):
            found_files.update({fname: get_mtime(fname)
                                for fname in scan_dir(path)})
    found_files = [(fname, mtime)
                   for (fname, mtime) in found_files.items()
                   if mtime >= minepoch]

    return [fname for fname, mtime in
            sorted(found_files, key=lambda x: x[1])[:howmany]]


def generate(spec):
    '''
    resolves audiospec-randomdir

    Recognized arguments:
        - path [mandatory]    source dir
        - maxage [default=ignored]  max age of audio files to pick
    '''
    for attr in ('path', 'maxage'):
        if attr not in spec:
            raise ValueError("Malformed audiospec: missing '%s'" % attr)

    if spec['maxage'].strip():
        try:
            maxage = int(spec['maxage'])
        except ValueError:
            maxage = timeparse(spec['maxage'])
            if maxage is None:
                raise ValueError("Unknown format for maxage: '{}'"
                                 .format(spec['maxage']))
            assert type(maxage) is int
    else:
        maxage = None

    now = int(time.time())
    minepoch = 0 if maxage is None else now - maxage

    picked = recent_choose([spec['path']], 1, minepoch)

    for path in picked:
        tmp = mkstemp(suffix=os.path.splitext(path)[-1],
                      prefix='randomdir-%s-' % shortname(path))
        os.close(tmp[0])
        shutil.copy(path, tmp[1])
        log.info("copying %s -> %s", path, os.path.basename(tmp[1]))
        yield 'file://{}'.format(tmp[1])


generate.description = 'Select most recent file inside a directory'
