from django.contrib import messages
from django.shortcuts import redirect, render, reverse
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page

from legal.generic import TemplateView


@method_decorator(cache_page(432000 * 60), name='dispatch')
class Confidentialite(TemplateView):
    http_method_names = ['get']
    template_name = 'pages/privacy.html'


@method_decorator(cache_page(432000 * 60), name='dispatch')
class CGV(TemplateView):
    http_method_names = ['get']
    template_name = 'pages/sale.html'


# @method_decorator(cache_page(432000 * 60), name='dispatch')
class CGU(TemplateView):
    http_method_names = ['get']
    template_name = 'pages/use.html'
