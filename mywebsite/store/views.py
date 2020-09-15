from django.http import Http404
from django.shortcuts import render
from django.utils.translation import gettext_lazy as _
from django.views.generic import DetailView, ListView

from store import models

class BaseDetailView(DetailView):
    model = models.Store
    store_name_field = 'storename'
    context_object_name = 'products'

    def get_object(self, queryset=None):
        if queryset is None:
            queryset = self.get_queryset()

        pk = self.kwargs.get(self.pk_url_kwarg)
        store_name = self.kwargs.get(self.store_name_field)

        if pk is not None and store_name is not None:
            queryset = queryset.filter(pk=pk, name=store_name)

        if pk is None and store_name is None:
            raise AttributeError('')

        try:
            obj = queryset.get()
        except queryset.model.DoesNotExist:
            raise Http404(_("No %(verbose_name)s found matching the query") %
                          {'verbose_name': queryset.model._meta.verbose_name})
        return obj


class StoresView(ListView):
    model = models.Store
    template_name = 'pages/stores.html'
    context_object_name = 'stores'

    def get_queryset(self):
        return self.model.objects.get()


class StoreView(BaseDetailView):
    template_name = 'pages/store.html'
