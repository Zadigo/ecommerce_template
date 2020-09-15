from django.template.context import RequestContext, Context


class Legal(Context):
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

    def __init__(self, **kwargs):
        super().__init__()
        print(self.__dict__)

    def cnil(self, url=None):
        return 'https://cnil.fr/'


def context(request):
    return Legal()
