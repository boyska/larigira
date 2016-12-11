import pytest

from .unused import UnusedCleaner
from .config import get_conf


@pytest.fixture
def unusedcleaner():
    return UnusedCleaner(get_conf(prefix='LARIGIRATEST_'))


# this test suite heavily assumes that TMPDIR == /tmp/, which is the default
# indeed.  However, the code does not rely on this assumption.

def test_watch_file(unusedcleaner):
    # despite not existing, the file is added
    unusedcleaner.watch('file:///tmp/gnam')
    assert len(unusedcleaner.waiting_removal_files) == 1
    assert list(unusedcleaner.waiting_removal_files)[0] == '/tmp/gnam'


def test_watch_path_error(unusedcleaner):
    '''paths are not valid thing to watch. URIs only, thanks'''
    unusedcleaner.watch('/tmp/foo')
    assert len(unusedcleaner.waiting_removal_files) == 0


def test_watch_notmp_error(unusedcleaner):
    '''Files not in TMPDIR are not added'''
    unusedcleaner.watch('file:///not/in/tmp')
    assert len(unusedcleaner.waiting_removal_files) == 0
