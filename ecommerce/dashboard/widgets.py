"""Custom widgets created specifically to fit the
boostrap syntax
"""

from django.forms import widgets

class TextInput(widgets.TextInput):
    template_name = 'widgets/textinput.html'

    def get_context(self, name, value, attrs):
        if attrs is None:
            attrs = dict()
        attrs['class'] = 'form-control'
        context = super().get_context(name, value, attrs)
        return context

class NumberInput(widgets.NumberInput):
    template_name = 'widgets/textinput.html'

    def get_context(self, name, value, attrs):
        if attrs is None:
            attrs = dict()
        attrs['class'] = 'form-control'
        context = super().get_context(name, value, attrs)
        return context

class Textarea(widgets.Textarea):
    template_name = 'widgets/textarea.html'

    def get_context(self, name, value, attrs):
        if attrs is None:
            attrs = dict()
        attrs['class'] = 'form-control'
        context = super().get_context(name, value, attrs)
        return context

class CheckBoxInput(widgets.CheckboxInput):
    template_name = 'widgets/checkbox.html'

    def get_context(self, name, value, attrs):
        if self.check_test(value):
            attrs = {**(attrs or {}), 'checked': True}
        attrs['class'] = 'custom-control-input'
        context = super().get_context(name, value, attrs)
        return context

class SelectInput(widgets.Select):
    template_name = 'widgets/select.html'

    def get_context(self, name, value, attrs):
        if attrs is None:
            attrs = dict()
        attrs['class'] = 'form-control'
        context = super().get_context(name, value, attrs)
        return context

class DateInput(widgets.DateInput):
    template_name = 'widgets/textinput.html'
    input_type = 'date'

    def get_context(self, name, value, attrs):
        if attrs is None:
            attrs = dict()
        attrs['class'] = 'form-control'
        context = super().get_context(name, value, attrs)
        return context

class FileInput(widgets.FileInput):
    template_name = 'widgets/file.html'

    def get_context(self, name, value, attrs):
        if attrs is None:
            attrs = dict()
        attrs['class'] = 'custom-file-input'
        context = super().get_context(name, value, attrs)
        return context
