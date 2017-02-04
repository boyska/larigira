import os
import logging
import shutil
import random
from tempfile import mkstemp

from larigira.fsutils import scan_dir, shortname
log = logging.getLogger(__name__)


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

    found_files = set()
    for path in spec['paths']:
        if not os.path.exists(path):
            log.warning("Can't find requested path: %s", path)
            continue
        if os.path.isfile(path):
            found_files.add(path)
        elif os.path.isdir(path):
            found_files.update(scan_dir(path))

    picked = random.sample(found_files, int(spec['howmany']))

    for path in picked:
        tmp = mkstemp(suffix=os.path.splitext(path)[-1],
                      prefix='randomdir-%s-' % shortname(path))
        os.close(tmp[0])
        shutil.copy(path, tmp[1])
        log.info("copying %s -> %s", path, os.path.basename(tmp[1]))
        yield 'file://{}'.format(tmp[1])


generate.description = 'Picks random files from a specified directory'
