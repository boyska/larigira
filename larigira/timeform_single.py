from datetime import datetime

from flask_wtf import Form
from wtforms import StringField, Field, validators, SubmitField
import wtforms.widgets


class DateTimeInput(wtforms.widgets.Input):
    input_type = 'datetime-local'


class EasyDateTimeField(Field):
    '''
    a "fork" of DateTimeField which uses HTML5 datetime-local
    The format is not customizable, because it is imposed by the HTML5 specification
    '''
    widget = DateTimeInput()

    def __init__(self, label=None, validators=None, **kwargs):
        super(EasyDateTimeField, self).__init__(label, validators, **kwargs)
        self.format = '%Y-%m-%dT%H:%M:%S'

    def _value(self):
        if self.raw_data:
            return ' '.join(self.raw_data)
        else:
            return self.data and self.data.strftime(self.format) or ''

    def process_formdata(self, valuelist):
        if valuelist:
            date_str = ' '.join(valuelist)
            try:
                self.data = datetime.strptime(date_str, self.format)
            except ValueError:
                self.data = None
                raise ValueError(self.gettext('Not a valid datetime value <tt>{}</tt>').format(date_str))



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
