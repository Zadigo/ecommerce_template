from django.shortcuts import render
from django.views.generic import View



class CustomerServiceView(View):
    def get(self, request, *args, **kwargs):
        links = [
            {'page': 'orders', 'icon': 'shopping_cart', 'title': 'Commande'},
            {'page': 'returns', 'icon': 'flight_landing', 'title': 'Retour'},
            {'page': 'delivery', 'icon': 'flight_takeoff', 'title': 'Livraison'},
        ]
        template = 'pages/customer_service.html'

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
            messages.error(
                request, "Le message n'a pas pu être envoyé car des champs sont manquants")
            return redirect('customer_care')

        if len(message) < 50:
            messages.error(
                request, "Votre message doit faire au moins 50 charactères", extra_tags='alert-warning')
            return redirect('customer_care')

        authorized_reasons = ['where', 'missing', 'refund', 'payment-question',
                              'defectuous', 'refund-duration', 'other']

        if reason not in authorized_reasons:
            messages.error(
                request, "Une erreur s'est produite - CUS-RE", extra_tags='alert-warning')
            return redirect('customer_care')

        try:
            send_mail(
                f"Customer Care - From: {email} - Order: {order}",
                message=message,

                from_email='contact.mywebsite@gmail.com',
                recipient_list=[
                    'contact.mywebsite@gmail.com'
                ],
                html_message="""
                Bonjour,


                """
            )
        except:
            messages.error(
                request, "Une erreur s'est produite - CUS-NS", extra_tags='alert-warning')
            return redirect('customer_care')

        messages.error(request, "Merci de nous avoir contacter",
                       extra_tags='alert-success')
        return redirect('customer_care')
