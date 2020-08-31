from django.forms import widgets


class CustomInput(widgets.Input):
    def get_context(self, name, value, attrs):
        if attrs is None:
            attrs = dict()
        attrs['class'] = 'form-control'
        context = super().get_context(name, value, attrs)
        return context


class TextInput(CustomInput):
    template_name = 'widgets/input.html'
    input_type = 'text'


class EmailInput(CustomInput):
    input_type = 'email'


class TelephoneInput(TextInput):
    input_type = 'tel'

    def get_context(self, name, value, attrs):
        if attrs is None:
            attrs = dict()
        attrs['class'] = 'form-control'
        attrs['autocomplete'] = 'tel'
        context = super().get_context(name, value, attrs)
        return context


class FirstNameInput(TextInput):
    def get_context(self, name, value, attrs):
        if attrs is None:
            attrs = dict()
        attrs['class'] = 'form-control'
        attrs['autocomplete'] = 'given-name'
        context = super().get_context(name, value, attrs)
        return context


class LastNameInput(TextInput):
    def get_context(self, name, value, attrs):
        if attrs is None:
            attrs = dict()
        attrs['class'] = 'form-control'
        attrs['autocomplete'] = 'family-name'
        context = super().get_context(name, value, attrs)
        return context


class AddressLineOne(TextInput):
    def get_context(self, name, value, attrs):
        if attrs is None:
            attrs = dict()
        attrs['class'] = 'form-control'
        attrs['autocomplete'] = 'street-address'
        context = super().get_context(name, value, attrs)
        return context
