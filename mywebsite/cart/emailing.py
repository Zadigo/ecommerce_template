from django.conf import settings
from django.contrib.sites.shortcuts import get_current_site
from django.core import exceptions
from django.core.mail import EmailMultiAlternatives
from django.template import loader


class ConfirmationEmails:
    subject_template_name = 'components/emails/email_subject.txt'
    email_template_name = None

    def send_email(self, context, from_email, to_email, html_template_name=None):
        """
        Main entrypoint for sending emails
        """
        if not self.email_template_name:
            raise ValueError('You must specify an email template name.')

        subject = loader.render_to_string(self.subject_template_name, context)
        subject = ''.join(subject.splitlines())

        body = loader.render_to_string(self.email_template_name, context)
        email = EmailMultiAlternatives(subject, body, from_email=from_email, to=[to_email])
        
        if html_template_name is not None:
            html_email = loader.render_to_string(html_template_name, context)
            email.attach(html_email, 'text/html')
        email.send()

    def process(self, request, to_email, **kwargs):
        from_email = self._get_email_host_user()
        self.send_email(self._check_kwargs(kwargs), from_email, to_email)

    def _get_email_host_user(self):
        try:
            return settings.EMAIL_HOST_USER
        except:
            raise ValueError('You should set an EMAIL_HOST_USER')

    @staticmethod
    def _check_kwargs(values):
        required = [
            'estimated_order_date',
            'customer_delivery_address',
            'order_reference',
            'order_quantity',
            'order_total',
            'customer_name'
        ]
        for item in required:
            keys = values.keys()
            if item not in keys:
                values.update({item: 'NOT_SET'})
        return values


class OrderConfirmationEmail(ConfirmationEmails):
    email_template_name = 'components/emails/confirmation_email.html'


class ExpeditionEmail(ConfirmationEmails):
    email_template_name = 'components/emails/expedition_email.html'


class FailedOrderEmail(ConfirmationEmails):
    email_template_name = 'components/emails/failed_email.html'

    def process(self, request, order_reference, transaction, customer_name):
        context = {
            'order_reference': order_reference,
            'transaction': transaction,
            'customer_name': customer_name
        }
        email_host_user = self._get_email_host_user()
        self.send_email(context, email_host_user, email_host_user)
