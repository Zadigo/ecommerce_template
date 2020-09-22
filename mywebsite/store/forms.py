from django import forms

class DashboardSettingsForm(forms.ModelForm):
    class Meta:
        model = dashboard_models.DashboardSetting
        fields = ['name', 'contact_email', 'customer_care_email',
                  'automatic_archive', 'allow_coupons', 'legal_name', 'telephone']
        widgets = {
            'name': custom_widgets.TextInput(),
            'contact_email': custom_widgets.EmailInput(),
            'customer_care_email': custom_widgets.EmailInput(),
            'automatic_archive': custom_widgets.CheckBoxInput(),
            'legal_name': custom_widgets.TextInput(),
            'telephone': custom_widgets.TextInput(),
        }
