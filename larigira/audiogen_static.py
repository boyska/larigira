import os
import logging
import shutil
from tempfile import mkstemp


def generate(spec):
    '''
    resolves audiospec-static

    Recognized argument is  "paths" (list of static paths)
    '''
    if 'paths' not in spec:
        raise ValueError("Malformed audiospec: missing 'paths'")

    for path in spec['paths']:
        if not os.path.exists(path):
            logging.warn("Can't find requested path: %s" % path)
            continue
        tmp = mkstemp(suffix=os.path.splitext(path)[-1],
                      prefix='audiogen-static-')
        os.close(tmp[0])
        shutil.copy(path, tmp[1])
        yield 'file://{}'.format(tmp[1])
generate.description = 'Picks always the same specified file'
