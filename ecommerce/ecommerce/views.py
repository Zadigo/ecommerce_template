from django import http
from django.conf import settings
from django.shortcuts import render
from django.views import generic
from django.views.decorators import csrf


class HeroView(generic.TemplateView):
    template_name = 'pages/home/hero.html'

def subscribe_user(request, **kwargs):
    pass

@csrf.csrf_exempt
def report_csp(request, **kwargs):
    """View for receiving CSP reports on the violation of
    content that would be injected on the page
    """
    import datetime

    reports_file_path = settings.REPORTS_FILE
    report = request.POST.get('report')

    current_date = datetime.datetime.now()

    report_format = f'[{current_date}] - - '

    # Write the report in a special file 
    # present in the media folder
    if report is not None:
        with open(reports_file_path, 'a+', encoding='utf-8') as f:
            f.writelines(report_format)
            f.writelines("\n")

            response = {
                'report': 'CSP report successful'
            }
    return http.JsonResponse(response, status=200)

class Confidentialite(generic.TemplateView):
    template_name = 'pages/legal/confidentialite.html'

class CustomerServiceView(generic.View):
    def get(self, request, *args, **kwargs):
        links = [
            {'page': 'orders', 'icon': 'shopping_cart', 'title': 'Commande'},
            {'page': 'returns', 'icon': 'flight_landing', 'title': 'Retour'},
            {'page': 'delivery', 'icon': 'flight_takeoff', 'title': 'Livraison'},
        ]
        template = 'pages/legal/customer_service.html'
        if 'page_name' in kwargs:
            page_name = kwargs['page_name']
            if page_name == 'orders':
                template = 'pages/legal/faq/orders.html'
            elif page_name == 'delivery':
                template = 'pages/legal/faq/delivery.html'
            elif page_name == 'returns':
                template = 'pages/legal/faq/returns.html'
        return render(request, template, context={'links': links})

class CGV(generic.TemplateView):
    template_name = 'pages/legal/cgv.html'

    def get_context_data(self):
        # from nawoka.company import Company

        context = super().get_context_data()
        # other = {
        #     'services': 'vente de produits de mode (sacs et accessoires)',
        #     'validity_date': '31-12-2019',
        #     'return_delay': '14 jours'
        # }
        # context = Company(context, 'Nawoka', 'contact.nawoka@gmail.com', '-', \
        #             '-', 'https://nawoka.fr', **other)
        return context

class CGU(generic.TemplateView):
    template_name = 'pages/legal/cgu.html'

    def get_context_data(self):
        # from nawoka.company import Company

        context = super().get_context_data()
        # other = {
        #     'services': 'vente de produits de mode (sacs et accessoires)',
        #     'return_delay': '5 jours'
        # }
        # context = Company(context, 'Nawoka', 'contact.nawoka@gmail.com', '0668552975', \
        #             '36 rue de Suède, 59000, Lille', 'https://nawoka.fr', **other)
        return context



def handler404(request, exception):
    return render(request, 'errors/error-404.html')

def handler500(request):
    return render(request, 'errors/error-500.html')
