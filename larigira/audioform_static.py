from __future__ import print_function

from flask_wtf import Form
from wtforms import StringField, validators, SubmitField


class StaticAudioForm(Form):
    nick = StringField(u'Audio nick', validators=[validators.required()],
                       description='A simple name to recognize this audio')
    path = StringField(u'Path', validators=[validators.required()],
                       description='Full path to audio file')
    submit = SubmitField(u'Submit')


def staticaudio_receive(form):
    return {
        'kind': 'static',
        'nick': form.nick.data,
        'paths': [form.path.data]
    }
