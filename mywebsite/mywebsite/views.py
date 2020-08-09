from django import http
from django.conf import settings
from django.contrib import messages
from django.core.mail import send_mail
from django.shortcuts import redirect, render
from django.utils.decorators import method_decorator
from django.views import generic
from django.views.decorators import csrf
from django.views.decorators import http as view_decorators

from mywebsite import forms


class HeroView(generic.TemplateView):
    template_name = 'pages/home/hero.html'

@view_decorators.require_POST
def subscribe_user(request, **kwargs):
    pass

@csrf.csrf_exempt
@view_decorators.require_POST
def report_csp(request, **kwargs):
    """View for receiving CSP reports on the violation of
    content that would be injected on the page
    """
    pass

class Confidentialite(generic.TemplateView):
    http_method_names = ['get']
    template_name = 'pages/legal/confidentialite.html'

class CustomerServiceView(generic.View):
    def get(self, request, *args, **kwargs):
        links = [
            {'page': 'orders', 'icon': 'shopping_cart', 'title': 'Commande'},
            {'page': 'returns', 'icon': 'flight_landing', 'title': 'Retour'},
            {'page': 'delivery', 'icon': 'flight_takeoff', 'title': 'Livraison'},
        ]
        template = 'pages/customer_care/customer_service.html'

        if 'page_name' in kwargs:
            page_name = kwargs['page_name']
            if page_name == 'orders':
                template = 'pages/customer_care/faq/orders.html'
            elif page_name == 'delivery':
                template = 'pages/customer_care/faq/delivery.html'
            elif page_name == 'returns':
                template = 'pages/customer_care/faq/returns.html'

        context = {
            'links': links,
        }
            
        return render(request, template, context=context)

    def post(self, request, **kwargs):
        email = request.POST.get('email')
        reason = request.POST.get('reason')
        order = request.POST.get('order')
        message = request.POST.get('message')

        if not email or not reason \
                or not order or not message:
            messages.error(request, "Le message n'a pas pu être envoyé car des champs sont manquants")
            return redirect('customer_care')

        if len(message) < 50:
            messages.error(request, "Votre message doit faire au moins 50 charactères", extra_tags='alert-warning')
            return redirect('customer_care')

        authorized_reasons = ['where', 'missing', 'refund', 'payment-question', 
                'defectuous', 'refund-duration', 'other']

        if reason not in authorized_reasons:
            messages.error(request, "Une erreur s'est produite - CUS-RE", extra_tags='alert-warning')
            return redirect('customer_care')

        try:
            send_mail(
                f"Customer Care - From: {email} - Order: {order}",
                message = message,

                from_email='contact.mywebsite@gmail.com',
                recipient_list = [
                    'contact.mywebsite@gmail.com'
                ],
                html_message = """
                Bonjour,


                """
            )
        except:
            messages.error(request, "Une erreur s'est produite - CUS-NS", extra_tags='alert-warning')
            return redirect('customer_care')

        messages.error(request, "Merci de nous avoir contacter", extra_tags='alert-success')
        return redirect('customer_care')

        

class CGV(generic.TemplateView):
    http_method_names = ['get']
    template_name = 'pages/legal/cgv.html'

class CGU(generic.TemplateView):
    http_method_names = ['get']
    template_name = 'pages/legal/cgu.html'

def handler404(request, exception):
    return render(request, 'pages/errors/error-404.html')

def handler500(request):
    return render(request, 'pages/errors/error-500.html')
