import tempfile
import os

from gevent import monkey
monkey.patch_all(subprocess=True)

import pytest

from larigira.event import EventModel


@pytest.yield_fixture
def db():
    fname = tempfile.mktemp(suffix='.json', prefix='larigira-test')
    yield EventModel(uri=fname)
    os.unlink(fname)


def test_empty(db):
    assert len(db.get_all_alarms()) == 0


def test_add_basic(db):
    assert len(db.get_all_alarms()) == 0
    alarm_id = db.add_event(dict(kind='frequency', interval=60*3, start=1),
                            [dict(kind='mpd', paths=['foo.mp3'], howmany=1)])
    assert len(db.get_all_alarms()) == 1
    assert db.get_alarm_by_id(alarm_id) is not None
    assert len(tuple(db.get_actions_by_alarm(
        db.get_alarm_by_id(alarm_id)))) == 1


def test_add_multiple_alarms(db):
    assert len(db.get_all_alarms()) == 0
    alarm_id = db.add_event(dict(kind='frequency', interval=60*3, start=1),
                            [dict(kind='mpd', paths=['foo.mp3'], howmany=1),
                             dict(kind='foo', a=3)])
    assert len(db.get_all_alarms()) == 1
    assert db.get_alarm_by_id(alarm_id) is not None
    assert len(db.actions.all()) == 2
    assert len(tuple(db.get_actions_by_alarm(
        db.get_alarm_by_id(alarm_id)))) == 2


def test_delete_alarm(db):
    assert len(db.get_all_alarms()) == 0
    alarm_id = db.add_event(dict(kind='frequency', interval=60*3, start=1),
                            [dict(kind='mpd', paths=['foo.mp3'], howmany=1)])
    action_id = next(db.get_actions_by_alarm(db.get_alarm_by_id(alarm_id))).eid
    assert len(db.get_all_alarms()) == 1
    db.delete_alarm(alarm_id)
    assert len(db.get_all_alarms()) == 0  # alarm deleted
    assert db.get_action_by_id(action_id) is not None
    assert 'kind' in db.get_action_by_id(action_id)  # action still there


def test_delete_alarm_nonexisting(db):
    with pytest.raises(KeyError):
        db.delete_alarm(123)


def test_delete_action(db):
    alarm_id = db.add_event(dict(kind='frequency', interval=60*3, start=1),
                            [dict(kind='mpd', paths=['foo.mp3'], howmany=1)])
    alarm = db.get_alarm_by_id(alarm_id)
    assert len(tuple(db.get_actions_by_alarm(alarm))) == 1
    action = next(db.get_actions_by_alarm(alarm))
    action_id = action.eid
    db.delete_action(action_id)
    assert len(tuple(db.get_actions_by_alarm(alarm))) == 0
