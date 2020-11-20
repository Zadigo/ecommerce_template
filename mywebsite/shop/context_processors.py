import logging
from functools import lru_cache
from importlib import import_module

from django.template.context import Context


@lru_cache
def get_shop_module(name='shop'):
    try:
        module = import_module(name)
    except ImportError:
        logging.info(f"The module {name} could not be found.")
        return None
    else:
        return module.__dict__()


class MyShop:
    brand = None
    email = None
    legal_name = None

    def __init__(self, **kwargs):
        kwargs.update(**self.__dict__())
        self.context = Context(kwargs)

    def get_context(self):
        return self.context


def shop_context_processors(request):
    items = get_shop_module()
    processors = []
    for key, item in items.items():
        if not key.startswith('__'):
            if callable(item) and issubclass(item, MyShop):
                processors.append(item)
    
    if not processors:
        processor = MyShop(request=request)
        return processor.get_context().flatten()
    else:
        final_dict = {}
        for processor in processors:
            instance = processor(request=request)
            final_dict.update(**instance.getcontext().flatten())
        return final_dict
