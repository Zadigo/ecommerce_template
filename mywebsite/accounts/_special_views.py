from django.core.exceptions import ImproperlyConfigured
from django.http.response import HttpResponseRedirect
from django.views.generic.base import ContextMixin, TemplateResponseMixin
from django.views.generic.edit import FormMixin, ProcessFormView


class MultipleFormsMixin(ContextMixin):
    initials = {}
    forms = {}
    success_url = None
    prefix = None

    def get_initial(self, name):
        """Return the initial data to use for forms on this view."""
        initial = self.initials.get(name, None)
        return initial.copy()

    def get_prefix(self):
        """Return the prefix to use for forms."""
        return self.prefix

    def get_form(self, form_name):
        try:
            form_class = self.forms[form_name]
        except:
            raise ValueError("You should provide a list of forms to use for your view")
        else:
            return form_class(**self.get_form_kwargs())

    def get_forms(self, at_index=None):
        if self.forms:
            forms = list(self.forms.values())
            if at_index is not None:
                if isinstance(at_index, int):
                    return forms[at_index]
            return forms
        return []

    def get_form_kwargs(self, form_name):
        """Return the keyword arguments for instantiating the form."""
        kwargs = {
            'initial': self.get_initial(form_name),
            'prefix': self.get_prefix(),
        }

        if self.request.method in ('POST', 'PUT'):
            kwargs.update({
                'data': self.request.POST,
                'files': self.request.FILES,
            })
        return kwargs

    def get_success_url(self):
        """Return the URL to redirect to after processing a valid form."""
        if not self.success_url:
            raise ImproperlyConfigured("No URL to redirect to. Provide a success_url.")
        return str(self.success_url)

    def form_valid(self, form):
        """If the form is valid, redirect to the supplied URL."""
        return HttpResponseRedirect(self.get_success_url())

    def form_invalid(self, form):
        """If the form is invalid, render the invalid form."""
        return self.render_to_response(self.get_context_data(form=form))

    def get_context_data(self, **kwargs):
        """Insert the forms into the context dict"""
        for key, form in self.forms.items():
            if key not in kwargs:
                kwargs[key] = form
        return super().get_context_data(**kwargs)


class BaseMultipleFormView(MultipleFormsMixin, ProcessFormView):
    form_selector_name = 'form_name'

    def post(self, request, *args, **kwargs):
        form = self.get_form(request.POST.get(self.form_selector_name))
        if form.is_valid():
            return self.form_valid(form)
        else:
            return self.form_invalid(form)

class MultipleFormView(TemplateResponseMixin, BaseMultipleFormView):
    """A view for managing post requests for multiple forms on a same view"""


class IndexView(MultipleFormView):
    form_selector_name = 'form_name'
    forms = {
        'form1': '',
        'form2': '',
        'form3': ''
    }

    def get(self, request, *args, **kwargs):
        context = super().get_context_data(**kwargs)
        self.get_form('form1')(
            initial= {
                
            }
        )
        return render()
