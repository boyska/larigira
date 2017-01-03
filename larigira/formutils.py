from wtforms.fields import StringField
import wtforms.widgets


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
