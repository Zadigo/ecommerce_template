from django.views.generic.list import (BaseListView,
                                       MultipleObjectTemplateResponseMixin)
from django.http import HttpResponseRedirect
from django.shortcuts import reverse
from cart import payment

class BaseCartView(MultipleObjectTemplateResponseMixin, BaseListView):
    """
    This is the base class for implement functonnalities to views
    that require functionnalities for e-commerce payments
    """
    cart_filters = {}
    empty_cart_url = '/no-cart'
    context_object_name = 'products'

    def dispatch(self, request, *args, **kwargs):
        redirect_url = self.empty_cart_url or reverse('cart:no_cart')
        if not self.get_queryset().exists():
            return HttpResponseRedirect(redirect_url)
        return super().dispatch(request, *args, **kwargs)

    def get_queryset(self):
        if self.queryset is None:
            queryset = self.model._default_manager.all()
        else:
            queryset = self.queryset
        return queryset.filter(user=self.request.user)

