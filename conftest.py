from gevent.queue import Queue
import pytest


@pytest.fixture
def queue():
    print('fixture q')
    return Queue()
