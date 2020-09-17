from django import http
from django.conf import settings
from django.contrib import messages
from django.core.mail import send_mail
from django.shortcuts import redirect, render
from django.utils.decorators import method_decorator
from django.views import generic
from django.views.decorators import csrf
from django.views.decorators import http as view_decorators


@csrf.csrf_exempt
@view_decorators.require_POST
def report_csp(request, **kwargs):
    """View for receiving CSP reports on the violation of
    content that would be injected on the page
    """
    pass


def handler404(request, exception):
    return render(request, 'pages/errors/error-404.html')


def handler500(request):
    return render(request, 'pages/errors/error-500.html')
