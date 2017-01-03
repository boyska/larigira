import flask_wtf
from wtforms import StringField, validators, SubmitField, IntegerField

from larigira.formutils import AutocompleteStringField


class Form(flask_wtf.Form):
    nick = StringField('Audio nick', validators=[validators.required()],
                       description='A simple name to recognize this audio')
    path = AutocompleteStringField('dl-suggested-dirs',
                                   'Path', validators=[validators.required()],
                                   description='Full path to source directory')
    howmany = IntegerField('Number', validators=[validators.optional()],
                           default=1,
                           description='How many songs to be picked'
                           'from this dir; defaults to 1')
    submit = SubmitField('Submit')

    def populate_from_audiospec(self, audiospec):
        if 'nick' in audiospec:
            self.nick.data = audiospec['nick']
        if 'paths' in audiospec:
            self.path.data = audiospec['paths'][0]
        if 'howmany' in audiospec:
            self.howmany.data = audiospec['howmany']
        else:
            self.howmany.data = 1


def receive(form):
    return {
        'kind': 'randomdir',
        'nick': form.nick.data,
        'paths': [form.path.data],
        'howmany': form.howmany.data or 1
    }

