from flask_wtf import Form
from wtforms import StringField, validators, SubmitField, ValidationError


class ScriptAudioForm(Form):
    nick = StringField(u'Audio nick', validators=[validators.required()],
                       description='A simple name to recognize this audio')
    name = StringField(u'Name', validators=[validators.required()],
                       description='filename (NOT path) of the script')
    args = StringField(u'Arguments',
                       description='arguments, separated by spaces')
    submit = SubmitField(u'Submit')

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
