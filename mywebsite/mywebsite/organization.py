from django.template import Context
from legal.context_processors import Legal


class Organization:
    name = None
    legal_name = None
    brand = None

    def __init__(self, **kwargs):
        kwargs.update(
            {
                'name': self.name,
                'legal_name': self.legal_name,
                'brand': self.brand,
                'website_name': self.name
            }
        )
        self.kwargs = kwargs

    def __call__(self, request):
        c = Context(self.kwargs)
        return c.flatten()

    @classmethod
    def get_context(cls, request):
        instance = cls()
        c = Context(instance.kwargs)
        return c.flatten()


class Nawoka(Legal):
    legal_name = 'Nawoka'

    def __init__(self):
        super().__init__(google='Talent')
