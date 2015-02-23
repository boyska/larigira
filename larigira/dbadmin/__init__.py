'''
This module contains a flask blueprint for db administration stuff

Templates are self-contained in this directory
'''
from __future__ import print_function

from flask import current_app, Blueprint, render_template, jsonify, abort

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


@db.route('/add/time/<kind>')
def addtime_kind(kind):
    Form = next(forms.get_timeform(kind))
    return render_template('add_time_kind.html', form=Form(), kind=kind)


@db.route('/add/time/<kind>', methods=['POST'])
def addtime_kind_post(kind):
    Form, receiver = tuple(forms.get_timeform(kind))
    form = Form()
    del Form
    if not form.validate_on_submit():
        abort(400)
    data = receiver(form)
    model = current_app.larigira.monitor.source.model
    eid = model.add_alarm(data)
    return jsonify(dict(inserted=eid, data=data))


@db.route('/add/audio')
def addaudio():
    kinds = get_avail_entrypoints('larigira.audioform_create')
    return render_template('add_audio.html', kinds=kinds)


@db.route('/add/audio/<kind>')
def addaudio_kind(kind):
    Form = next(forms.get_audioform(kind))
    return render_template('add_audio_kind.html', form=Form(), kind=kind)


@db.route('/add/audio/<kind>', methods=['POST'])
def addaudio_kind_post(kind):
    Form, receiver = tuple(forms.get_audioform(kind))
    form = Form()
    del Form
    if not form.validate_on_submit():
        abort(400)
    data = receiver(form)
    model = current_app.larigira.monitor.source.model
    eid = model.add_action(data)
    return jsonify(dict(inserted=eid, data=data))
