import logging

from datetime import datetime
from pytimeparse.timeparse import timeparse

from flask_wtf import Form
from wtforms import StringField, validators, SubmitField, \
        SelectMultipleField, ValidationError

from larigira.formutils import EasyDateTimeField
log = logging.getLogger(__name__)


class SingleAlarmForm(Form):
    nick = StringField('Alarm nick', validators=[validators.required()],
                       description='A simple name to recognize this alarm')
    dt = EasyDateTimeField('Date and time', validators=[validators.required()],
                           description='Date to ring on, expressed as '
                           '2000-12-31T13:42:00')
    submit = SubmitField('Submit')

    def populate_from_timespec(self, timespec):
        if 'nick' in timespec:
            self.nick.data = timespec['nick']
        if 'timestamp' in timespec:
            self.dt.data = datetime.fromtimestamp(timespec['timestamp'])


def singlealarm_receive(form):
    return {
        'kind': 'single',
        'nick': form.nick.data,
        'timestamp': int(form.dt.data.strftime('%s'))
    }


class FrequencyAlarmForm(Form):
    nick = StringField('Alarm nick', validators=[validators.required()],
                       description='A simple name to recognize this alarm')
    interval = StringField('Frequency',
                           validators=[validators.required()],
                           description='in seconds, or human-readable '
                           '(like 9w3d12h)')
    start = EasyDateTimeField('Start date and time',
                              validators=[validators.optional()],
                              description='Before this, no alarm will ring. '
                              'Expressed as YYYY-MM-DDTHH:MM:SS. If omitted, '
                              'the alarm will always ring')
    end = EasyDateTimeField('End date and time',
                            validators=[validators.optional()],
                            description='After this, no alarm will ring. '
                            'Expressed as YYYY-MM-DDTHH:MM:SS. If omitted, '
                            'the alarm will always ring')
    weekdays = SelectMultipleField('Days on which the alarm should be played',
                                   choices=[('1', 'Monday'),
                                            ('2', 'Tuesday'),
                                            ('3', 'Wednesday'),
                                            ('4', 'Thursday'),
                                            ('5', 'Friday'),
                                            ('6', 'Saturday'),
                                            ('7', 'Sunday')],
                                   default=list('1234567'),
                                   validators=[validators.required()],
                                   description='The alarm will ring only on '
                                   'selected weekdays')
    submit = SubmitField('Submit')

    def populate_from_timespec(self, timespec):
        if 'nick' in timespec:
            self.nick.data = timespec['nick']
        if 'start' in timespec:
            self.start.data = datetime.fromtimestamp(timespec['start'])
        if 'end' in timespec:
            self.end.data = datetime.fromtimestamp(timespec['end'])
        if 'weekdays' in timespec:
            self.weekdays.data = timespec['weekdays']
        else:
            self.weekdays.data = list('1234567')
        self.interval.data = timespec['interval']

    def validate_interval(self, field):
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
        'weekdays': form.weekdays.data,
    }
    if form.start.data:
        obj['start'] = int(form.start.data.strftime('%s'))
    else:
        obj['start'] = 0
    if form.end.data:
        obj['end'] = int(form.end.data.strftime('%s'))
    return obj
