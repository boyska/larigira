from __future__ import print_function

from flask_wtf import Form
from wtforms import StringField, DateTimeField, IntegerField, validators, \
        SubmitField


class FrequencyAlarmForm(Form):
    nick = StringField(u'Alarm nick', validators=[validators.required()],
                       description='A simple name to recognize this alarm')
    start = DateTimeField(u'Start date and time',
                          validators=[validators.required()],
                          description='Date before which no alarm will ring, '
                          'expressed as YYYY-MM-DD HH:MM:SS')
    end = DateTimeField(u'End date and time',
                        validators=[validators.optional()],
                        description='Date after which no alarm will ring, '
                        'expressed as YYYY-MM-DD HH:MM:SS')
    interval = IntegerField(u'Frequency',
                            validators=[validators.required()],
                            description='in seconds')
    submit = SubmitField(u'Submit')


def frequencyalarm_receive(form):
    obj = {
        'kind': 'frequency',
        'nick': form.nick.data,
        'start': int(form.start.data.strftime('%s')),
        'interval': form.interval.data,
    }
    if form.end.data:
        obj['end'] = int(form.end.data.strftime('%s'))
    return obj

