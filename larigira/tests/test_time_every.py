from datetime import timedelta, datetime
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
    return datetime.now()


@pytest.fixture(params=['seconds', 'human', 'humanlong', 'coloned'])
def onehour(now, request):
    '''a FrequencyAlarm: every hour for one day'''
    intervals = dict(seconds=3600, human='1h', humanlong='30m 1800s',
                     coloned='01:00:00')
    return FrequencyAlarm({
        'start': now - timedelta(days=1),
        'interval': intervals[request.param],
        'end': now + days(1)})

@pytest.fixture(params=[1, '1'])
def onehour_monday(request):
    monday = request.param
    yield FrequencyAlarm({
        'interval': 3600*12,
        'weekdays': [monday],  # mondays only
        'start': 0
    })


@pytest.fixture(params=['seconds', 'human', 'coloned'])
def tenseconds(now, request):
    '''a FrequencyAlarm: every 10 seconds for one day'''
    intervals = dict(seconds=10, human='10s', coloned='00:10')
    return FrequencyAlarm({
        'start': now - timedelta(days=1),
        'interval': intervals[request.param],
        'end': now + days(1)})


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


def test_freq_short(now, tenseconds):
    f = tenseconds
    assert now in f.all_rings(now - days(3))
    assert f.next_ring(now) is not None
    assert f.next_ring(now) != now
    assert f.next_ring(now) > now
    assert now not in f.all_rings(now)
    for r in f.all_rings(now):
        assert r > now


@pytest.mark.timeout(1)
def test_freq_ring(now, onehour):
    f = onehour
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


def test_weekday_skip(onehour_monday):
    t = datetime.fromtimestamp(0)
    for _ in range(20):  # 20 is an arbitrary number
        t = onehour_monday.next_ring(t)
        print(_, t, t.isoweekday())
        assert t.isoweekday() == 1  # monday; don't get confused by .weekday()


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
