from __future__ import print_function
from gevent import monkey
monkey.patch_all(subprocess=True)

import pytest

import gevent

from larigira.mpc import Timer, ParentedLet

# TODO: implement simple children and check that we will receive the expected
# messages on the queue


@pytest.fixture
def range_parentlet():
    class RangeLet(ParentedLet):
        def __init__(self, howmany, queue):
            ParentedLet.__init__(self, queue)
            self.howmany = howmany

        def do_business(self):
            for i in range(self.howmany):
                yield('range', i)
    return RangeLet


@pytest.fixture
def single_value_parentlet():
    class SingleLet(ParentedLet):
        def __init__(self, val, queue):
            ParentedLet.__init__(self, queue)
            self.val = val

        def do_business(self):
            yield('single', self.val)
    return SingleLet


def test_parented_range(queue, range_parentlet):
    t = range_parentlet(5, queue)
    t.start()
    gevent.sleep(0.01)
    assert queue.qsize() == 5
    while not queue.empty():
        msg = queue.get()
        assert msg['kind'] == 'range'


def test_parented_single(queue, single_value_parentlet):
    t = single_value_parentlet(123, queue)
    t.start()
    gevent.sleep(0.01)
    msg = queue.get_nowait()
    assert msg['args'][0] == 123


def test_timer_finally(queue):
    '''at somepoint, it will get results'''
    period = 10
    t = Timer(period, queue)
    t.start()
    gevent.sleep(period*3/1000.0)
    queue.get_nowait()


def test_timer_righttime(queue):
    '''not too early, not too late'''
    period = 500
    t = Timer(period, queue)
    t.start()
    gevent.sleep(period/(10*1000.0))
    assert queue.empty() is True
    gevent.sleep(period*(2/1000.0))
    assert not queue.empty()
    queue.get_nowait()
