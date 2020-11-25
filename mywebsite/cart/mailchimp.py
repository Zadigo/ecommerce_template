from functools import cached_property

import mailchimp_transactional as MailchimpTransactional
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.template.context import Context
from mailchimp_transactional.api_client import ApiClientError


def get_mail_chimp_api_key():
    try:
        return settings.MAILCHIMP_API_KEY
    except:
        raise ImproperlyConfigured(
            'Please provide a valid MAILCHIMP_API_KEY in your settings file')


# @cached_property
def get_mailchimp_client():
    return MailchimpTransactional.Client(get_mail_chimp_api_key())







class Mailchimp:
    def __init__(self):
        self.api_key = get_mail_chimp_api_key()

    @classmethod
    def get_api_key(cls, request):
        instance = cls()
        c = Context({'mailchimp_api_key': instance.api_key})
        return c.flatten()


class Transactional(Mailchimp):
    def __init__(self):
        self.client = MailchimpTransactional.Client(self.api_key)

    @classmethod
    def test_transactional_api(cls):
        instance = cls()
        try:
            _ = instance.cilent.users.ping()
        except ApiClientError as error:
            return False
        else:
            return True

    def send_transactional_email(self, message):
        message = {
            "from_email": "manny@mailchimp.com",
            "subject": "Hello world",
            "text": "Welcome to Mailchimp Transactional!",
            "to": [
                {
                    "email": "freddie@example.com",
                    "type": "to"
                }
            ]
        }
        return self.client.messages.send(message)
