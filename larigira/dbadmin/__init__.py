'''
This module contains a flask blueprint for db administration stuff

Templates are self-contained in this directory
'''
from __future__ import print_function

from flask import current_app, Blueprint, render_template, jsonify, abort, \
    request, redirect, url_for

from larigira.entrypoints_utils import get_avail_entrypoints
from larigira import forms
db = Blueprint('db', __name__, url_prefix='/db', template_folder='templates')


@db.route('/')
def home():
    return render_template('dbadmin_base.html')


@db.route('/list')
def list():
    model = current_app.larigira.monitor.source.model
    alarms = tuple(model.get_all_alarms())
    events = [(alarm, model.get_actions_by_alarm(alarm))
              for alarm in alarms]
    return render_template('list.html', events=events)


@db.route('/add/time')
def addtime():
    kinds = get_avail_entrypoints('larigira.timeform_create')
    return render_template('add_time.html', kinds=kinds)


@db.route('/add/time/<kind>', methods=['GET', 'POST'])
def addtime_kind(kind):
    Form, receiver = tuple(forms.get_timeform(kind))
    form = Form()
    if request.method == 'POST' and form.validate():
        data = receiver(form)
        model = current_app.larigira.monitor.source.model
        eid = model.add_alarm(data)
        return redirect(url_for('db.edit_event', alarmid=eid))

    return render_template('add_time_kind.html', form=form, kind=kind)


@db.route('/add/audio')
def addaudio():
    kinds = get_avail_entrypoints('larigira.audioform_create')
    return render_template('add_audio.html', kinds=kinds)


@db.route('/add/audio/<kind>', methods=['GET', 'POST'])
def addaudio_kind(kind):
    Form, receiver = tuple(forms.get_audioform(kind))
    form = Form()
    if request.method == 'POST' and form.validate():
        data = receiver(form)
        model = current_app.larigira.monitor.source.model
        eid = model.add_action(data)
        return jsonify(dict(inserted=eid, data=data))

    return render_template('add_audio_kind.html', form=form, kind=kind)


@db.route('/edit/event/<alarmid>')
def edit_event(alarmid):
    model = current_app.larigira.monitor.source.model
    alarm = model.get_alarm_by_id(int(alarmid))
    if alarm is None:
        abort(404)
    allactions = model.get_all_actions()
    print('all', allactions)
    actions = tuple(model.get_actions_by_alarm(alarm))
    return render_template('edit_event.html',
                           alarm=alarm, all_actions=allactions,
                           actions=actions)


@db.route('/api/alarm/<alarmid>/actions', methods=['POST'])
def change_actions(alarmid):
    new_actions = request.form.getlist('actions[]')
    if new_actions is None:
        new_actions = []
    model = current_app.larigira.monitor.source.model
    ret = model.update_alarm(int(alarmid),
                             new_fields={'actions': map(int, new_actions)})
    return jsonify(dict(updated=alarmid, ret=ret))
