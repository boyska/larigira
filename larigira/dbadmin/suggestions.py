import os

from flask import current_app

from larigira.config import get_conf
from larigira.fsutils import scan_dir_audio


def get_suggested_files():
    if not get_conf()['FILE_PATH_SUGGESTION']:
        return []
    if current_app.cache.has('dbadmin.get_suggested_files'):
        return current_app.cache.get('dbadmin.get_suggested_files')
    current_app.logger.debug('get_suggested_files MISS in cache')
    files = []
    for path in get_conf()['FILE_PATH_SUGGESTION']:
        if not os.path.isdir(path):
            current_app.logger.warning('Invalid suggestion path: %s' % path)
            continue
        pathfiles = scan_dir_audio(path)
        files.extend(pathfiles)
    current_app.logger.debug('Suggested files: %s' % ', '.join(files))

    current_app.cache.set('dbadmin.get_suggested_files', files,
                          timeout=600)  # ten minutes
    return files


def get_suggested_dirs():
    dirset = set()
    for f in get_suggested_files():
        dirpath = os.path.dirname(f)
        while dirpath:
            if dirpath in dirset:
                break
            dirset.add(dirpath)
            dirpath = os.path.dirname(dirpath)

    return list(dirset)


def get_suggested_scripts():
    base = get_conf()['SCRIPTS_PATH']
    if not base or not os.path.isdir(base):
        return []
    fnames = [f for f in os.listdir(base)
              if os.access(os.path.join(base, f), os.R_OK | os.X_OK)]
    return fnames


def get_suggestions():
    files = get_suggested_files()
    if len(files) > 200:
        current_app.logger.warning("Too many suggested files, cropping")
        files = files[:200]
    return dict(
        files=files,
        dirs=get_suggested_dirs(),
        scripts=get_suggested_scripts(),
    )


