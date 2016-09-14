from flask_wtf import Form
from wtforms import StringField, validators, SubmitField, ValidationError


class ScriptAudioForm(Form):
    nick = StringField('Audio nick', validators=[validators.required()],
                       description='A simple name to recognize this audio')
    name = StringField('Name', validators=[validators.required()],
                       description='filename (NOT path) of the script')
    args = StringField('Arguments',
                       description='arguments, separated by spaces')
    submit = SubmitField('Submit')

    def populate_from_audiospec(self, audiospec):
        if 'nick' in audiospec:
            self.nick.data = audiospec['nick']
        if 'name' in audiospec:
            self.name.data = audiospec['name']
        if 'args' in audiospec:
            self.args.data = audiospec['args']

    def validate_name(form, field):
        if '/' in field.data:
            raise ValidationError("Name cannot have slashes: "
                                  "it's a name, not a path")


def scriptaudio_receive(form):
    return {
        'kind': 'script',
        'nick': form.nick.data,
        'name': form.name.data,
        'args': form.args.data
    }
