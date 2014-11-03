from datetime import timedelta
from pprint import pprint

import pytest

from larigira.timegen_every import FrequencyAlarm, SingleAlarm
from larigira.timegen import timegenerate


def eq_(a, b, reason=None):
    '''migrating tests from nose'''
    if reason is not None:
        assert a == b, reason
    else:
        assert a == b


@pytest.fixture
def now():
    from datetime import datetime
    return datetime.now()


def days(n):
    return timedelta(days=n)


def test_single_creations(now):
    return SingleAlarm({
        'timestamp': now
    })


def test_freq_creations(now):
    return FrequencyAlarm({
        'start': now - timedelta(days=1),
        'interval': 3600,
        'end': now})


@pytest.mark.timeout(1)
def test_single_ring(now):
    dt = now + days(1)
    s = SingleAlarm({'timestamp': dt})
    eq_(s.next_ring(),  dt)
    eq_(s.next_ring(now),  dt)
    assert s.next_ring(dt) is None, "%s - %s" % (str(s.next_ring(dt)), str(dt))
    assert s.next_ring(now + days(2)) is None
    assert s.has_ring(dt)
    assert not s.has_ring(now)
    assert not s.has_ring(now + days(2))


@pytest.mark.timeout(1)
def test_single_all(now):
    dt = now + timedelta(days=1)
    s = SingleAlarm({'timestamp': dt})
    eq_(list(s.all_rings()),  [dt])
    eq_(list(s.all_rings(now)),  [dt])
    eq_(list(s.all_rings(now + days(2))),  [])


def test_freq_short(now):
    f = FrequencyAlarm({
        'start': now - days(1),
        'interval': 10,
        'end': now + days(1)
    })
    assert now in f.all_rings(now - days(3))
    assert f.next_ring(now) is not None
    assert f.next_ring(now) != now
    assert f.next_ring(now) > now
    assert now not in f.all_rings(now)
    for r in f.all_rings(now):
        assert r > now


@pytest.mark.timeout(1)
def test_freq_ring(now):
    f = FrequencyAlarm({
        'start': now - days(1),
        'interval': 3600,
        'end': now + days(1)
    })
    assert now in f.all_rings(now - days(3))
    assert f.next_ring(now) is not None
    assert f.next_ring(now) != now
    assert f.next_ring(now) > now
    assert now not in f.all_rings(now)
    for r in f.all_rings(now):
        assert r > now
    allr = list(f.all_rings(now))
    eq_(len(allr), 24)

    eq_(len(tuple(f.all_rings(now + days(2)))), 0)

    allr = tuple(f.all_rings(now - days(20)))
    eq_(f.next_ring(now - days(20)), now - days(1))
    eq_(len(allr), 49, pprint(allr))


def test_single_registered():
    timegenerate({
        'kind': 'single',
        'timestamp': 1234567890
    })


def test_frequency_registered():
    timegenerate({
        'kind': 'frequency',
        'start': 1234567890,
        'interval': 60*15
    })
