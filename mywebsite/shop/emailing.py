from django.contrib.auth import forms
from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import EmailMultiAlternatives
from django.template import loader
from django.core import exceptions


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

    def process(self, request, from_email, to_email, 
                estimated_order_date, customer_delivery_address, 
                order_reference, order_quantity, customer_name=None, **kwargs):
        context = {
            'estimated_order_date': estimated_order_date,
            'customer_delivery_address': customer_delivery_address,
            'order_reference': order_reference,
            'order_quantity': order_quantity,
            'customer_name': customer_name,
            **kwargs
        }
        self.send_email(context, from_email, to_email)


class OrderConfirmationEmail(ConfirmationEmails):
    email_template_name = 'components/emails/confirmation_email.html'


class ExpeditionEmail(ConfirmationEmails):
    email_template_name = 'components/emails/expedition_email.html'
