"""Custom widgets created specifically to fit the
Boostrap or Materialize syntax
"""

from django.forms import widgets



class CustomInput(widgets.Input):
    def get_context(self, name, value, attrs):
        if attrs is None:
            attrs = dict()
        attrs['class'] = 'form-control'
        context = super().get_context(name, value, attrs)
        return context


class VueCustomInput(widgets.Input):
    def get_context(self, name, value, attrs):
        if attrs is None:
            attrs = dict()
        attrs['class'] = 'form-control'
        attrs['v-model'] = name
        context = super().get_context(name, value, attrs)
        return context


class TextInput(CustomInput):
    template_name = 'widgets/input.html'
    input_type = 'text'


class NumberInput(CustomInput):
    template_name = 'widgets/input.html'
    input_type = 'number'
    

class Textarea(CustomInput):
    template_name = 'widgets/textarea.html'


class CheckBoxInput(widgets.CheckboxInput):
    # template_name = 'widgets/checkbox.html'
    template_name = 'widgets/input.html'

    def get_context(self, name, value, attrs):
        if self.check_test(value):
            attrs = {**(attrs or {}), 'checked': True}
        attrs['class'] = 'custom-control-input'
        context = super().get_context(name, value, attrs)
        context['label_name'] = 'Fast'
        return context


class LabeledCheckBoxInput(CheckBoxInput):
    template_name = 'widgets/labeled_checkbox.html'

class SelectInput(CustomInput):
    template_name = 'widgets/select.html'


class DateInput(CustomInput):
    template_name = 'widgets/input.html'
    input_type = 'date'


class FileInput(widgets.FileInput):
    template_name = 'widgets/file.html'
    input_type = 'file'

    def get_context(self, name, value, attrs):
        if attrs is None:
            attrs = dict()
        attrs['class'] = 'custom-file-input'
        context = super().get_context(name, value, attrs)
        return context


class EmailInput(CustomInput):
    template_name = 'widgets/input.html'
    input_type = 'email'


class VueTextInput(VueCustomInput):
    template_name = 'widgets/vue_textinput.html'
    input_type = 'text'
