from django import forms

class AnalyticsSettingsForm(forms.ModelForm):
    class Meta:
        model = dashboard_models.DashboardSetting
        fields = ['google_analytics', 'google_tag_manager',
                  'google_optimize', 'google_ads', 'facebook_pixels', 'mailchimp']
        widgets = {
            'google_analytics': custom_widgets.TextInput(),
            'google_tag_manager': custom_widgets.TextInput(),
            'google_optimize': custom_widgets.TextInput(),
            'google_ads': custom_widgets.TextInput(),
            'facebook_pixels': custom_widgets.TextInput(),
            'mailchimp': custom_widgets.TextInput(),
        }

    def clean(self):
        # UA-148220996-1 / GTM-WXVG7KF / AW-701852005 / 191877658898691
        data = self.cleaned_data
        if data['google_analytics']:
            is_match = re.match(r'UA\-\d{9}\-\d{1}', data['google_analytics'])
            if not is_match:
                raise forms.ValidationError(
                    'The Google Analytics tag is not valid')
        if data['google_tag_manager']:
            is_match = re.match(
                r'GTM\-[A-Z0-9]{7}', data['google_tag_manager'])
            if not is_match:
                raise forms.ValidationError(
                    'The Google Tag manager tag is not valid')
        return data
