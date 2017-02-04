import os
import logging
import shutil
from tempfile import mkstemp

from larigira.fsutils import shortname
log = logging.getLogger(__name__)


def generate(spec):
    '''
    resolves audiospec-static

    Recognized argument is  "paths" (list of static paths)
    '''
    if 'paths' not in spec:
        raise ValueError("Malformed audiospec: missing 'paths'")

    for path in spec['paths']:
        if not os.path.exists(path):
            log.warning("Can't find requested path: %s", path)
            continue
        tmp = mkstemp(suffix=os.path.splitext(path)[-1],
                      prefix='static-%s-' % shortname(path))
        os.close(tmp[0])
        log.info("copying %s -> %s", path, os.path.basename(tmp[1]))
        shutil.copy(path, tmp[1])
        yield 'file://{}'.format(tmp[1])


generate.description = 'Picks always the same specified file'
