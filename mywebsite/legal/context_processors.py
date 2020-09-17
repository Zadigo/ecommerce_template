from django.template.context import RequestContext, Context


class Legal:
    legal_name = None
    address = None
    domain = None
    email = None
    telephone = None
    services = None
    available_days = None
    shipping_details = None
    shipping_company = None
    return_policy = None

    def __init__(self, google=None):
        self.google = google

    def cnil(self, url=None):
        return 'https://cnil.fr/'


def context_processor(request):
    context = RequestContext(request)
    legal = Legal()
    print(legal.legal_name)
    return {}
