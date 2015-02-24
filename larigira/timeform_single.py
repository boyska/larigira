from __future__ import print_function

from flask_wtf import Form
from wtforms import StringField, DateTimeField, validators, SubmitField


class SingleAlarmForm(Form):
    nick = StringField(u'Alarm nick', validators=[validators.required()],
                       description='A simple name to recognize this alarm')
    dt = DateTimeField(u'Date and time', validators=[validators.required()],
                       description='Date to ring on, expressed as '
                       'YYYY-MM-DD HH:MM:SS')
    submit = SubmitField(u'Submit')


def singlealarm_receive(form):
    return {
        'kind': 'single',
        'nick': form.nick.data,
        'timestamp': int(form.dt.data.strftime('%s'))
    }
