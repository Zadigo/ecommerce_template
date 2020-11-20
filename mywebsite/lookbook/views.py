from django.shortcuts import render
from django.views.generic import TemplateView

class LookBookView(TemplateView):
    """Base view for the website's lookbook"""
    template_name = 'pages/lookbook.html'
