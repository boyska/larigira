from pytimeparse.timeparse import timeparse
from flask_wtf import Form
from wtforms import StringField, validators, SubmitField, ValidationError

from larigira.formutils import AutocompleteStringField


class AudioForm(Form):
    nick = StringField('Audio nick', validators=[validators.required()],
                       description='A simple name to recognize this audio')
    path = AutocompleteStringField('dl-suggested-dirs',
                                   'Path', validators=[validators.required()],
                                   description='Directory to pick file from')
    maxage = StringField('Max age',
                         validators=[validators.required()],
                         description='in seconds, or human-readable '
                         '(like 9w3d12h)')
    submit = SubmitField('Submit')

    def validate_maxage(self, field):
        try:
            int(field.data)
        except ValueError:
            if timeparse(field.data) is None:
                raise ValidationError("maxage must either be a number "
                                      "(in seconds) or a human-readable "
                                      "string like '1h2m'  or '1d12h'")


def audio_receive(form):
    return {
        'kind': 'mostrecent',
        'nick': form.nick.data,
        'path': form.path.data,
        'maxage': form.maxage.data,
        'howmany': 1
    }
