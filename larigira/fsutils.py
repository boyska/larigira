import os
import fnmatch


def scan_dir(dirname, extension=None):
    if extension is None:
        extension = '*'
    for root, dirnames, filenames in os.walk(dirname):
        for fname in fnmatch.filter(filenames, extension):
            yield os.path.join(root, fname)


def multi_fnmatch(fname, extensions):
    for ext in extensions:
        if fnmatch.fnmatch(fname, '*.' + ext):
            return True
    return False


def scan_dir_audio(dirname, extensions=('mp3', 'oga', 'wav', 'ogg')):
    for root, dirnames, filenames in os.walk(dirname):
        for fname in filenames:
            if multi_fnmatch(fname, extensions):
                yield os.path.join(root, fname)


def shortname(path):
    name = os.path.basename(path)  # filename
    name = name.rsplit('.', 1)[0]   # no extension
    name = ''.join(c for c in name if c.isalnum())  # no strange chars
    return name
