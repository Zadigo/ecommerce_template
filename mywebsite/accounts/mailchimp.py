from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from hashlib import md5
from django.template.context import Context
from mailchimp_marketing import Client
from mailchimp_transactional.api_client import ApiClientError


def get_mail_chimp_api_key():
    try:
        return settings.MAILCHIMP_API_KEY
    except:
        raise ImproperlyConfigured('Please provide a valid MAILCHIMP_API_KEY in your settings file')


def get_mail_chimp_server_key():
    try:
        return settings.MAILCHIMP_SERVER_LINK
    except:
        raise ImproperlyConfigured('Please provide a valid MAILCHIMP_SERVER_LINK in your settings file')


def get_mailchimp_client():
    key = get_mail_chimp_api_key()
    server = get_mail_chimp_server_key()

    client = Client()
    client.set_config({
        'api_key': key,
        # https://us19.admin.mailchimp.com/...
        'server': server
    })
    return client















class Mailchimp:
    def __init__(self):
        self.api_key = get_mail_chimp_api_key()

    @classmethod
    def get_api_key(cls, request):
        instance = cls()
        c = Context({'mailchimp_api_key': instance.api_key})
        return c.flatten()

class Marketing(Mailchimp):
    def __init__(self):
        client = Client()
        client.set_config({
            'api_key': self.api_key,
            # https://us19.admin.mailchimp.com/...
            'server': get_mail_chimp_server_key()
        })
        self.client = client

    def create_list_body(self, from_name, from_email, subject, **kwargs):
        kwargs.update({
            'permission_reminder': 'You signed up for updates on our website',
            'email_type_option': False,
            'campaign_defaults': {
                'from_name': from_name,
                'from_email': from_email,
                'subject': subject,
                'language': 'EN_US'
            }
        })
        contact = kwargs.get('contact', None)
        if contact is None:
            kwargs.setdefault('contact', {
                'company': 'Mailchimp',
                'address1': '675 Ponce de Leon Ave NE',
                'address2': 'Suite 5000',
                'city': 'Atlanta',
                'state': 'GA',
                'zip': '30308',
                'country': 'FR'
            })
        return kwargs

    def create_audience(self, body=None, from_name=None, from_email=None, subject=None, **kwargs):
        # body = {
        #     "permission_reminder": "You signed up for updates on our website",
        #     "email_type_option": False,
        #     "campaign_defaults": {
        #         "from_name": "Mailchimp",
        #         "from_email": "freddie@mailchimp.com",
        #         "subject": "Python Developers",
        #         "language": "EN_US"
        #     },
        #     "name": "JS Developers Meetup",
        #     "contact": {
        #         "company": "Mailchimp",
        #         "address1": "675 Ponce de Leon Ave NE",
        #         "address2": "Suite 5000",
        #         "city": "Atlanta",
        #         "state": "GA",
        #         "zip": "30308",
        #         "country": "US"
        #     }
        # }
        body = body or self.create_list_body(
            from_name, from_email, subject, **kwargs)
        if body is None:
            url = 'https://mailchimp.com/developer/guides/create-your-first-audience/'
            raise TypeError(
                f'Provide a valid body object in order to create a new list in mailchimp: {url}')
        try:
            return self.client.lists.create_list(body)
        except ApiClientError as e:
            print(e.text)

    def add_member(self, list_id, email, firstname, lastname):
        member_info = {
            'email_address': 'prudence.mcvankab@example.com',
            'status': 'subscribed',
            'merge_fields': {
                'FNAME': 'Prudence',
                'LNAME': 'McVankab'
            }
        }
        try:
            return self.client.lists.add_list_member(list_id, member_info)
        except ApiClientError as e:
            print(e.text)

    def unsubscribe_member(self, list_id, email):
        # list_id = "YOUR_LIST_ID"
        # member_email = "MEMBER_EMAIL_ADDRESS"
        member_email_hash = md5(email.encode('utf-8')).hexdigest()
        member_update = {'status': 'unsubscribed'}
        try:
            return self.client.lists.update_list_member(list_id, member_email_hash, member_update)
        except ApiClientError as e:
            print(e.text)
