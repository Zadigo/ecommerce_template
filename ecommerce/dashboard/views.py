from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.paginator import Paginator
from django.db.models.expressions import Q
from django.http.response import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render, reverse
from django.utils.decorators import method_decorator
from django.views import generic
from django.views.decorators.csrf import csrf_exempt
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from dashboard import forms
from shop import models, serializers, utilities

MYUSER = get_user_model()


class IndexView(LoginRequiredMixin, generic.View):
    def get(self, request, *args, **kwargs):
        context = {
            'carts_count': models.Cart.statistics.total_count(),
            'orders_count': models.CustomerOrder.statistics.total_count(),
            'latest_orders': models.CustomerOrder.statistics.latest_orders(),
            'revenue': models.CustomerOrder.statistics.revenue()
        }
        return render(request, 'pages/home.html', context)

class ProductsView(LoginRequiredMixin, generic.ListView):
    model = models.Product
    queryset = models.Product.objects.all()
    template_name = 'pages/list.html'
    context_object_name = 'products'
    paginate_by = 10

class UsersView(LoginRequiredMixin, generic.ListView):
    model = MYUSER
    queryset = MYUSER.objects.all()
    template_name = 'pages/users.html'
    context_object_name = 'users'
    paginate_by = 10

class UserView(LoginRequiredMixin, generic.DetailView):
    model = MYUSER
    queryset = MYUSER.objects.all()
    template_name = 'pages/profile.html'
    context_object_name = 'user'

class SearchView(LoginRequiredMixin, generic.ListView):
    model = models.Product
    template_name = 'pages/search/products.html'
    context_object_name = 'products'
    paginate_by = 10

    def get_queryset(self):
        queryset = super().get_queryset()
        searched_item = self.request.GET.get('s')

        items = queryset.filter(Q(name__icontains=searched_item) 
            | Q(reference__icontains=searched_item) 
            | Q(collection__collection_name__icontains=searched_item)
        )

        return items

class ProductView(LoginRequiredMixin, generic.DetailView):
    """The details of a specific product
    """
    model = models.Product
    queryset = models.Product.objects.all()
    template_name = 'pages/details.html'
    context_object_name = 'product'

    def get_context_data(self, **kwargs):
        product = super().get_object()
        # We have to pass the user profile here
        # in order to get extra details on the user
        context = super().get_context_data()
        return context

class SingleProductOrdersView(LoginRequiredMixin, generic.ListView):
    """Orders for one single product
    """
    model   = models.CustomerOrder
    context_object_name = 'orders'
    template_name = 'pages/orders.html'

    def get_queryset(self):
        queryset = super().get_queryset()
        product = get_object_or_404(models.Product, id=self.kwargs['pk'])
        queryset = queryset.filter(reference=product.reference)
        return queryset

class ProductOrdersView(LoginRequiredMixin, generic.ListView):
    """All the orders made by customers for a specific company
    """
    model   = models.CustomerOrder
    queryset = models.CustomerOrder.objects.all()
    context_object_name = 'orders'
    template_name = 'pages/orders.html'

    def get_context_data(self):
        context = super().get_context_data()
        return context

class CreateProductView(LoginRequiredMixin, generic.View):
    max_number_of_steps = 3

    def get(self, request, *args, **kwargs):
        create_form_logic = forms.CreateFormLogic(request)
        return render(request, 'pages/create.html', create_form_logic.context)

    def post(self, request, **kwargs):
        create_form_logic = forms.CreateFormLogic(request)
        create_form_logic.instances = [['collection', 'collection_name', models.Collection]]
        url = create_form_logic.validate_form_and_update_model(models.Product, viewname='dashboard_create')
        return redirect(url)

class UpdateProductView(LoginRequiredMixin, generic.TemplateView):
    template_name = 'pages/update.html'
    
    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(**kwargs)
        product = get_object_or_404(models.Product, id=kwargs['pk'])
        context.update({'product': {'name': product.name}})
        return context

class CartsView(LoginRequiredMixin, generic.ListView):
    model = models.Cart
    queryset = models.Cart.objects.all()
    template_name = 'pages/carts.html'
    context_object_name = 'products'

class ImagesView(LoginRequiredMixin, generic.ListView):
    model = models.Image
    queryset = models.Image.objects.all()
    template_name = 'pages/images.html'
    context_object_name = 'images'
    paginate_by = 8

    def get_context_data(self, **kwargs):
        queryset = super().get_queryset()
        context = super().get_context_data(**kwargs)

        # Pagination for VueJS
        paginator = Paginator(queryset, 8)
        page = self.request.GET.get('page')
        images = paginator.get_page(page)
        images = serializers.ImageSerializer(instance=images.object_list, many=True)
        context['vue_images'] = images.data
        return context

@login_required
def deleteview(request, **kwargs):
    method = kwargs['method']
    if method == 'products':
        item = get_object_or_404(models.Product, id=kwargs['pk'])

    if method == 'carts':
        item = get_object_or_404(models.Cart, id=kwargs['pk'])

    item.delete()
    url = f'dashboard_{method}'
    return redirect(reverse(url))

class Settings(LoginRequiredMixin, generic.View):
    def get(self, request, *args, **kwargs):
        return render(request, 'settings.htm', {})


# CHARTS VIEWS


class BaseAPIView(APIView):
    authentication_classes = []
    permission_classes = []

class ChartsView(BaseAPIView):
    def get(self, format=None, **kwargs):
        payments_by_month = models.CustomerOrder\
                            .statistics.payments_by_month()
        print(payments_by_month)
        data = {
            "myChart": {
                'labels': payments_by_month[0],
                # 'labels': ["Red", "Blue", "Yellow", "Green", "Purple", "Orange"]
                # 'data': [4, 5, 15, 34, 12, 98]
                'data': payments_by_month[1]
            }
        }
        return Response(data=data[kwargs['name']])
