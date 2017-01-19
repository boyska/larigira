import logging

from wtforms.fields import StringField
from wtforms import Field
import wtforms.widgets

from datetime import datetime

log = logging.getLogger(__name__)


class AutocompleteTextInput(wtforms.widgets.Input):
    def __init__(self, datalist=None):
        super().__init__('text')
        self.datalist = datalist

    def __call__(self, field, **kwargs):
        # every second can be specified
        if self.datalist is not None:
            return super(AutocompleteTextInput, self).__call__(
                field, list=self.datalist, autocomplete="autocomplete",
                **kwargs)
        return super(AutocompleteTextInput, self).__call__(
            field, **kwargs)


class AutocompleteStringField(StringField):
    def __init__(self, datalist, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.widget = AutocompleteTextInput(datalist)


class DateTimeInput(wtforms.widgets.Input):
    input_type = 'datetime-local'

    def __call__(self, field, **kwargs):
        # every second can be specified
        return super(DateTimeInput, self).__call__(field, step='1', **kwargs)


class EasyDateTimeField(Field):
    '''
    a "fork" of DateTimeField which uses HTML5 datetime-local

    The format is not customizable, because it is imposed by the HTML5
    specification.

    This field does not ensure that browser actually supports datetime-local
    input type, nor does it provide polyfills.
    '''
    widget = DateTimeInput()
    formats = ('%Y-%m-%dT%H:%M:%S', '%Y-%m-%dT%H:%M')

    def __init__(self, label=None, validators=None, **kwargs):
        super(EasyDateTimeField, self).__init__(label, validators, **kwargs)

    def _value(self):
        if self.raw_data:
            return ' '.join(self.raw_data)
        return self.data and self.data.strftime(self.formats[0]) or ''

    def process_formdata(self, valuelist):
        if valuelist:
            date_str = ' '.join(valuelist)
            for fmt in self.formats:
                try:
                    self.data = datetime.strptime(date_str, fmt)
                    return
                except ValueError:
                    log.debug('Format `%s` not valid for `%s`',
                              fmt, date_str)
            raise ValueError(self.gettext(
                'Not a valid datetime value <tt>{}</tt>').format(date_str))
