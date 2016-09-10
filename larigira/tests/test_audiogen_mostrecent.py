import tempfile
import os
import time

import pytest

from larigira.audiogen_mostrecent import recent_choose


@pytest.fixture
def now(request):
    return int(time.time())


@pytest.fixture
def empty_dir():
    dirpath = tempfile.mkdtemp(prefix='mostrecent.')
    yield dirpath
    os.removedirs(dirpath)


@pytest.fixture
def dir_with_old_file(empty_dir):
    fd, fname = tempfile.mkstemp(prefix='old.', dir=empty_dir)
    os.close(fd)
    os.utime(fname, times=(0, 0))
    yield empty_dir
    os.unlink(fname)


@pytest.fixture
def dir_with_new_file(dir_with_old_file, now):
    fd, fname = tempfile.mkstemp(prefix='new.', dir=dir_with_old_file)
    os.close(fd)
    os.utime(fname, times=(now, now))
    yield dir_with_old_file
    os.unlink(fname)


def test_empty_is_empty(empty_dir, now):
    '''nothing can be picked from a empty dir'''
    picked = recent_choose([empty_dir], 1, now)
    assert len(picked) == 0


def test_old_files(dir_with_old_file, now):
    picked = recent_choose([dir_with_old_file], 1, now)
    assert len(picked) == 0


def test_new_files_found(dir_with_new_file):
    picked = recent_choose([dir_with_new_file], 1, 1)
    assert len(picked) == 1
    assert os.path.basename(picked[0]).startswith('new.')


def test_only_new_files_found(dir_with_new_file):
    picked = recent_choose([dir_with_new_file], 2, 1)
    assert len(picked) == 1
    assert os.path.basename(picked[0]).startswith('new.')
