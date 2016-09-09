from datetime import datetime
from pytimeparse.timeparse import timeparse
from flask_wtf import Form
from wtforms import StringField, DateTimeField, validators, \
        SubmitField, ValidationError


class FrequencyAlarmForm(Form):
    nick = StringField('Alarm nick', validators=[validators.required()],
                       description='A simple name to recognize this alarm')
    interval = StringField('Frequency',
                           validators=[validators.required()],
                           description='in seconds, or human-readable '
                           '(like 9w3d12h)')
    start = DateTimeField('Start date and time',
                          validators=[validators.optional()],
                          description='Date before which no alarm will ring, '
                          'expressed as YYYY-MM-DD HH:MM:SS; if omitted, the '
                          'alarm will always ring')
    end = DateTimeField('End date and time',
                        validators=[validators.optional()],
                        description='Date after which no alarm will ring, '
                        'expressed as YYYY-MM-DD HH:MM:SS; if omitted, the '
                        'alarm will always ring')
    submit = SubmitField('Submit')

    def populate_from_timespec(self, timespec):
        if 'nick' in timespec:
            self.nick.data = timespec['nick']
        if 'start' in timespec:
            self.start.data = datetime.fromtimestamp(timespec['start'])
        if 'end' in timespec:
            self.end.data = datetime.fromtimestamp(timespec['end'])
        self.interval.data = timespec['interval']

    def validate_interval(form, field):
        try:
            int(field.data)
        except ValueError:
            if timeparse(field.data) is None:
                raise ValidationError("interval must either be a number "
                                      "(in seconds) or a human-readable "
                                      "string like '1h2m'  or '1d12h'")


def frequencyalarm_receive(form):
    obj = {
        'kind': 'frequency',
        'nick': form.nick.data,
        'interval': form.interval.data,
    }
    if form.start.data:
        obj['start'] = int(form.start.data.strftime('%s'))
    else:
        obj['start'] = 0
    if form.end.data:
        obj['end'] = int(form.end.data.strftime('%s'))
    return obj
