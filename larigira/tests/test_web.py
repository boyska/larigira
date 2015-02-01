from __future__ import print_function
from gevent import monkey
monkey.patch_all(subprocess=True)

import pytest

from larigira.rpc import create_app
from larigira.larigira import Larigira


@pytest.fixture
def app(queue):
    return create_app(queue, Larigira())


def test_refresh(app):
    assert app.queue.empty()
    app.test_client().get('/api/refresh')
    assert not app.queue.empty()
