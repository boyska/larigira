from __future__ import print_function

from flask_wtf import Form
from wtforms import StringField, validators, SubmitField

from larigira.formutils import AutocompleteStringField


class StaticAudioForm(Form):
    nick = StringField('Audio nick', validators=[validators.required()],
                       description='A simple name to recognize this audio')
    path = AutocompleteStringField('dl-suggested-files',
                                   'Path', validators=[validators.required()],
                                   description='Full path to audio file')
    submit = SubmitField('Submit')

    def populate_from_audiospec(self, audiospec):
        if 'nick' in audiospec:
            self.nick.data = audiospec['nick']
        if 'paths' in audiospec:
            self.path.data = audiospec['paths'][0]


def staticaudio_receive(form):
    return {
        'kind': 'static',
        'nick': form.nick.data,
        'paths': [form.path.data]
    }
