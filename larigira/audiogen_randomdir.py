import os
import logging
import shutil
import random
from tempfile import mkstemp
import fnmatch


def scan_dir(dirname, extension=None):
    if extension is None:
        extension = '*'
    for root, dirnames, filenames in os.walk(dirname):
        for fname in fnmatch.filter(filenames, extension):
            yield os.path.join(root, fname)


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
            logging.warn("Can't find requested path: %s" % path)
            continue
        if os.path.isfile(path):
            found_files.add(path)
        elif os.path.isdir(path):
            found_files.update(scan_dir(path))

    picked = random.sample(found_files, int(spec['howmany']))

    for path in picked:
        tmp = mkstemp(suffix=os.path.splitext(path)[-1],
                      prefix='audiogen-randomdir-')
        os.close(tmp[0])
        shutil.copy(path, tmp[1])
        yield 'file://{}'.format(tmp[1])

generate.description = 'Picks random files from a specified directory'
