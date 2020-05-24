from django import forms
from django.forms import fields
from django.forms import widgets
from shop import utilities, models

class CreateForm1(forms.Form):
    name = fields.CharField(max_length=50, widget=widgets.TextInput(attrs={'placeholder': 'Nom du produit'}))
    price_ht = fields.IntegerField(min_value=0, widget=widgets.NumberInput(attrs={'placeholder': 'Prix HT'}))
    # collection = fields.ChoiceField(choices=models.ProductCollection.forms_manager.for_forms())
    reference = fields.CharField(initial=utilities.create_product_reference(), disabled=True)

class CreateForm2(forms.Form):
    description = fields.CharField(max_length=280, widget=widgets.Textarea(attrs={'placeholder': 'Description courte'}))

class CreateForm3(forms.Form):
    image = fields.FileField(widget=widgets.FileInput())

class CreateFormLogic:
    """This class implements a logic that allows to create and
    then update an object in the database step by step or,
    anywayws by following a specific set of steps.

    Parameters
    ----------

        instances: in many to many fields and foreign key fields, updating
        them requires an instance. By passing a list of list e.g.
        [[field, model]], the logic can iterate in order to substitute the
        raw data by the instance model.
    """
    available_forms = [CreateForm1, CreateForm2, CreateForm3]
    instances = []
    max_number_of_steps = 0
    current_step = 1

    def __init__(self, request, template_on_error=[], requires_instance=False):
        self.max_number_of_steps = len(self.available_forms)
        self.request = request
        self.context = {}
        self.requires_instance = requires_instance
        self.list_fitted_current_step = self.fit(self.current_step)

    def __setattr__(self, name, value):
        if name == 'request':
            if isinstance(value, (int, str)):
                current_step = int(value)
            else:
                step = value.GET.get('step')
                current_step = int(step) if step else 1
            self.__dict__['current_step'] = current_step
        return super().__setattr__(name, value)

    def __getattribute__(self, name):
        if name == 'context':
            if self.current_step == self.max_number_of_steps:
                self.__dict__[name]['final_step'] = True
            self.__dict__[name]['form'] = self.available_forms[self.list_fitted_current_step]
        return super().__getattribute__(name)

    def update_context(self, name, value):
        self.context.update({name: value})
        return self.context

    @property
    def next_step(self):
        return self.current_step + 1

    @property
    def get_context(self):
        return self.context

    @staticmethod
    def fit(current_step):
        """Fits the current step the list index since the step index
        is ahead of 1"""
        return current_step - 1

    @property
    def is_final_step(self):
        return self.current_step == self.max_number_of_steps

    def current_form(self):
        """Get the current loaded form"""
        try:
            form = self.available_forms[self.list_fitted_current_step]
        except:
            form = self.available_forms[0]
        return form

    def validate_form(self):
        form = self.current_form()(data=self.request.POST)
        return form if form.is_valid() else False

    def do_steps_alone(self, viewname):
        """Returns only the url for the steps without validating anything.
        This can be used for debugging purpses and to make sure the logic
        is able to move from steps to steps."""
        if not self.validate_form():
            forms.ValidationError('There was a problem validating the form')
            self.current_step_as_url(viewname)
        return self.next_step_as_url(viewname)
        
    def validate_form_and_update_model(self, model, viewname=None, debug_mode=False):
        """Updates a previous created product

        Description
        -----------

            Returns a valid view url to the next step
        
        Parameters
        ----------

            pop_from_session: on the final step, pops the id from the session
        """
        form_is_valid = self.validate_form()

        if not debug_mode:
            if form_is_valid and self.current_step == 1:
                # if self.requires_instance:
                #     for instance in self.instances:
                #         field = instance[0]
                #         model_field = instance[1]
                #         item = instance[2].objects.get(**{model_field: form_is_valid.cleaned_data[field]})
                #         # Now replace the raw data by the instance in the
                #         # cleaned data form fields
                #         form_is_valid.cleaned_data[field] = item
                form_is_valid.cleaned_data['collection'] = models.ProductCollection.\
                            objects.get(name=form_is_valid.cleaned_data['collection'])
                product = model.objects.create(**form_is_valid.cleaned_data)
                self.request.session['created_product_id'] = product.id

            try:
                # From step 2, we base the logic on whether there's a
                # created product id in the user's session, they can proceed
                # to continue editing the product...
                product_id = self.request.session['created_product_id']
            except KeyError:
                # By the moment there is none, then they
                # have to go through the first step
                return self.first_step_as_url('dashboard_create')

            if form_is_valid and self.current_step > 1:
                product_id = self.request.session['created_product_id']
                product = model.objects.filter(id=product_id)
                product.update(**form_is_valid.cleaned_data)
            elif self.current_step == self.max_number_of_steps:
                # product = model.objects.get(id=product_id)
                # product.update(**form_is_valid.cleaned_data)
                product_id = self.request.session.pop('created_product_id')
            else:
                pass

        if viewname and not self.is_final_step:
            return self.next_step_as_url(viewname)
        elif viewname and self.is_final_step:
            if debug_mode:
                product_id = 1
            # On the final step, just redirect to the product
            # itself -; or eventually the list of products
            return self.next_to_product('dashboard_product', product_id)
        
        return product
    
    def first_step_as_url(self, viewname):
        from django.shortcuts import reverse
        return f'{reverse(viewname)}?step=1'

    def current_step_as_url(self, viewname):
        """Returns the current step as a url"""
        from django.shortcuts import reverse
        return f'{reverse(viewname)}?step={self.current_step}'
    
    def next_step_as_url(self, viewname, pk=None):
        """Returns the next step as a URL"""
        from django.shortcuts import reverse
        return f'{reverse(viewname)}?step={self.next_step}'

    def next_to_product(self, viewname, pk):
        from django.shortcuts import reverse
        return reverse('dashboard_product', args=[pk])




class UpdateForm1(forms.ModelForm):
    class Meta:
        model = models.Product
        fields = ['name', 'collection', \
                    'price_ht', 'discount_pct', 'clothe_size']
        widgets = {
            'name': forms.widgets.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nom du produit'}),
            'collection': forms.widgets.Select(attrs={'class': 'form-control'}),
            'price_ht': forms.widgets.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Prix Hors Taxe', 'min': 0}),
            'discount_pct': forms.widgets.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Réduction (%)', 'min': 0, 'max': 100}),
            'clothe_size': forms.widgets.SelectMultiple(attrs={'class': 'custom-select'})
        }

    def clean(self):
        if 'price_ht' in self.cleaned_data or \
                'discount_pct' in self.cleaned_data:
            price_ht = self.cleaned_data['price_ht']
            discount_pct = self.cleaned_data['discount_pct']

            if price_ht < 0:
                raise forms.ValidationError('Price cannot be under 0')

            if discount_pct < 0 or discount_pct > 75:
                raise forms.ValidationError('Discount percentage cannot be below 0 and over 75%')
        return self.cleaned_data

class UpdateForm2(forms.ModelForm):
    class Meta:
        model = models.Product
        fields = ['description']
        widgets = {
            'description': forms.widgets.Textarea(attrs={'class': 'form-control'}),
        }
