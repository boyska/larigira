'''
This module contains a flask blueprint for db administration stuff

Templates are self-contained in this directory
'''
from __future__ import print_function

from flask import current_app, Blueprint, render_template, jsonify, abort, \
    request, redirect, url_for

from larigira.entrypoints_utils import get_avail_entrypoints
from larigira.audiogen import get_audiogenerator
from larigira.timegen import get_timegenerator
from larigira import forms
from .suggestions import get_suggestions
db = Blueprint('db', __name__, url_prefix='/db', template_folder='templates')


def get_model():
    return current_app.larigira.controller.monitor.model


@db.route('/')
def home():
    return render_template('dbadmin_base.html')


@db.route('/list')
def events_list():
    model = current_app.larigira.controller.monitor.model
    alarms = tuple(model.get_all_alarms())
    events = [(alarm, model.get_actions_by_alarm(alarm))
              for alarm in alarms]
    return render_template('list.html', events=events)


@db.route('/add/time')
def addtime():
    kinds = get_avail_entrypoints('larigira.timeform_create')

    def gen_info(gen):
        return dict(description=getattr(gen, 'description', ''))
    info = {kind: gen_info(get_timegenerator(kind))
            for kind in kinds}
    return render_template('add_time.html', kinds=kinds, info=info)


@db.route('/edit/time/<int:alarmid>', methods=['GET', 'POST'])
def edit_time(alarmid):
    model = get_model()
    timespec = model.get_alarm_by_id(alarmid)
    kind = timespec['kind']
    Form, receiver = tuple(forms.get_timeform(kind))
    form = Form()
    if request.method == 'GET':
        form.populate_from_timespec(timespec)
    if request.method == 'POST' and form.validate():
        data = receiver(form)
        model.update_alarm(alarmid, data)
        model.reload()
        return redirect(url_for('db.events_list',
                                _anchor='event-%d' % alarmid))
    return render_template('add_time_kind.html',
                           form=form,
                           kind=kind,
                           mode='edit',
                           )


@db.route('/add/time/<kind>', methods=['GET', 'POST'])
def addtime_kind(kind):
    Form, receiver = tuple(forms.get_timeform(kind))
    form = Form()
    if request.method == 'POST' and form.validate():
        data = receiver(form)
        eid = get_model().add_alarm(data)
        return redirect(url_for('db.edit_event', alarmid=eid))

    return render_template('add_time_kind.html',
                           form=form, kind=kind, mode='add')


@db.route('/add/audio')
def addaudio():
    kinds = get_avail_entrypoints('larigira.audioform_create')

    def gen_info(gen):
        return dict(description=getattr(gen, 'description', ''))
    info = {kind: gen_info(get_audiogenerator(kind))
            for kind in kinds}
    return render_template('add_audio.html', kinds=kinds, info=info)


@db.route('/add/audio/<kind>', methods=['GET', 'POST'])
def addaudio_kind(kind):
    Form, receiver = tuple(forms.get_audioform(kind))
    form = Form()
    if request.method == 'POST' and form.validate():
        data = receiver(form)
        model = current_app.larigira.controller.monitor.model
        eid = model.add_action(data)
        return jsonify(dict(inserted=eid, data=data))

    return render_template('add_audio_kind.html', form=form, kind=kind,
                           suggestions=get_suggestions()
                           )


@db.route('/edit/audio/<int:actionid>', methods=['GET', 'POST'])
def edit_audio(actionid):
    model = get_model()
    audiospec = model.get_action_by_id(actionid)
    kind = audiospec['kind']
    Form, receiver = tuple(forms.get_audioform(kind))
    form = Form()
    if request.method == 'GET':
        form.populate_from_audiospec(audiospec)
    if request.method == 'POST' and form.validate():
        data = receiver(form)
        model.update_action(actionid, data)
        model.reload()
        return redirect(url_for('db.events_list'))
    return render_template('add_audio_kind.html',
                           form=form,
                           kind=kind,
                           mode='edit',
                           suggestions=get_suggestions()
                           )


@db.route('/edit/event/<alarmid>')
def edit_event(alarmid):
    model = current_app.larigira.controller.monitor.model
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
    model = current_app.larigira.controller.monitor.model
    ret = model.update_alarm(int(alarmid),
                             new_fields={'actions': [int(a) for a in
                                                     new_actions]})
    return jsonify(dict(updated=alarmid, ret=ret))
