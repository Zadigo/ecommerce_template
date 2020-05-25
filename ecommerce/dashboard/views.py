from django import http
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.mail import send_mail, send_mass_mail
from django.core.paginator import Paginator
from django.db.models.expressions import F, Q
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
    template_name = 'pages/lists/list.html'
    context_object_name = 'products'
    paginate_by = 10

class ProductView(LoginRequiredMixin, generic.DetailView):
    """The details of a specific product
    """
    model = models.Product
    queryset = models.Product.objects.all()
    template_name = 'pages/details/product.html'
    context_object_name = 'product'

    def post(self, request, **kwargs):
        method = request.POST.get('method')
        if not method:
            return http.JsonResponse(data={'status': 'Ok.'}, status=202)

        product = super().get_object()

        if method == "images":
            uploaded_files = request.FILES['images']
            filename = uploaded_files.name
            true_name = utilities.get_image_name(filename)
            # data = uploaded_files.read()

            fake_url = 'https://mdbootstrap.com/img/Photos/Horizontal/E-commerce/Products/17.jpg'
            image = models.Image.objects.create(url=fake_url)
            product.name = true_name
            product.save()
            product.images.add(image)
            return http.JsonResponse({'status': 'Images updated'})
        
        if method == 'state':
            current_state = product.active
            if current_state == True:
                product.active = False
            else:
                product.active = True
            product.save()

        if method == 'reduction':
            current_state = product.discounted
            if current_state == True:
                product.discounted = False
            else:
                product.discounted = True
            product.save()

        if method == 'stock':
            current_state = product.in_stock
            if current_state == True:
                product.in_stock = False
            else:
                product.in_stock = True
            product.save()

        if method == 'association':
            product = super().get_object()
            images = request.POST.get('images')
            # When one value is selected, transform
            # the string into an array to simplify
            # the code
            print(images)
            if isinstance(images, str):
                images = [images]
            database_images = models.Image.objects.filter(name__in=images)
            print(database_images)
            if database_images:
                # product.images.set(database_images)
                product.images.clear()
                for image in database_images:
                    product.images.add(image)
            return redirect(reverse('dashboard_product', args=[product.id]))

        return http.JsonResponse({'status': 'Done'})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        product = super().get_object()
        context['additional_images'] = product.images.filter()
        context['images_form'] = forms.ImageAssociationForm(initial={'images': list(product.images.values_list('name', flat=True))})
        return context


class UsersView(LoginRequiredMixin, generic.ListView):
    model = MYUSER
    queryset = MYUSER.objects.all()
    template_name = 'pages/lists/users.html'
    context_object_name = 'users'
    paginate_by = 10

class UserView(LoginRequiredMixin, generic.DetailView):
    model = MYUSER
    queryset = MYUSER.objects.all()
    template_name = 'pages/details/profile.html'
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

class CustomerOrdersView(LoginRequiredMixin, generic.ListView):
    """All the orders made by customers for a specific company
    """
    model   = models.CustomerOrder
    queryset = models.CustomerOrder.objects.all()
    context_object_name = 'orders'
    template_name = 'pages/lists/orders.html'
    paginate_by = 10

    def get_context_data(self):
        context = super().get_context_data()
        return context

class ProductOrdersView(LoginRequiredMixin, generic.ListView):
    """Orders for one single product
    """
    model   = models.CustomerOrder
    context_object_name = 'orders'
    template_name = 'pages/lists/orders.html'

    def get_queryset(self):
        product = get_object_or_404(models.Product, id=self.kwargs['pk'])
        queryset = product.cart.product.all()
        return queryset

class CustomerOrderView(LoginRequiredMixin, generic.DetailView):
    """Orders for one single product
    """
    model   = models.CustomerOrder
    template_name = 'pages/details/order.html'
    context_object_name = 'order'

    def post(self, request, **kwargs):
        customerorder = super().get_object()
        if customerorder.completed:
            customerorder.completed = False
        else:
            customerorder.completed = True
        customerorder.save()
        return http.JsonResponse(data={'success': True})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        order = super().get_object()
        products = order.cart.product.all()
        if products.exists():
            context['products'] = products 
        return context

class CreateProductView(LoginRequiredMixin, generic.CreateView):
    model = models.Product
    form_class = forms.UpdateForm1
    template_name = 'pages/create/step1.html'
    context_object_name = 'product'

    def get_success_url(self):
        return reverse('dashboard_products')


    # max_number_of_steps = 3

    # def get(self, request, *args, **kwargs):
    #     create_form_logic = forms.CreateFormLogic(request)
    #     return render(request, 'pages/create.html', create_form_logic.context)

    # def post(self, request, **kwargs):
    #     create_form_logic = forms.CreateFormLogic(request)
    #     create_form_logic.instances = [['collection', 'collection_name', models.Collection]]
    #     url = create_form_logic.validate_form_and_update_model(models.Product, viewname='dashboard_create')
    #     return redirect(url)

class UpdateProductView(LoginRequiredMixin, generic.UpdateView):
    model = models.Product
    template_name = 'pages/update/step1.html'
    form_class = forms.UpdateForm1
    context_object_name = 'product'

    def post(self, request, *args, **kwargs):
        request = super().post(request, *args, **kwargs)
        # print(self.request.POST)
        # This section deals with the final
        # step of the update process by
        # redirecting to the correct view
        method = self.request.GET.get('step')
        if method == "2":
            return redirect('dashboard_products')
        return request

    def get_success_url(self):
        product = super().get_object()
        
        method = self.request.GET.get('step')

        if method is None:
            method = 0
        
        new_success_url = f'{reverse("update", args=[product.id])}?step={int(method) + 1}'

        if method != "2":
            return new_success_url

    def get_form_class(self):
        method = self.request.GET.get('step')
        if method is None:
            return self.form_class
        
        if method == "1":
            return forms.UpdateForm2
        return self.form_class

    def get_template_names(self):
        templates = super().get_template_names()
        method = self.request.GET.get('step')
        
        if method is None:
            return templates
        
        if method == "1":
            return ['pages/update/step2.html']
        elif method == "2":
            return ['pages/update/step3.html']

        return ['pages/list.html']

class CartsView(LoginRequiredMixin, generic.ListView):
    model = models.Cart
    queryset = models.Cart.objects.all()
    template_name = 'pages/lists/carts.html'
    context_object_name = 'products'
    paginate_by = 5

class ImagesView(LoginRequiredMixin, generic.ListView):
    model = models.Image
    queryset = models.Image.objects.all()
    template_name = 'pages/lists/images.html'
    context_object_name = 'images'
    paginate_by = 8

    def post(self, request, **kwargs):
        method = request.POST.get('method')
        if not method:
            return http.JsonResponse(data={'status': 'Understood'}, code=202)

        if method == 'delete':
            image_id = request.POST.get('image_id')
            if not image_id:
                return http.JsonResponse(data={'status': 'Ok.'}, code=202)
            image = self.queryset.get(id=int(image_id))
            if image_id:
                image.delete()
                return http.JsonResponse(data={'status': 'Success'})

        if method == 'imageurl':
            name = request.POST.get('name')
            variant = request.POST.get('variant')
            url = request.POST.get('url')
            self.model.objects.create(name=name, variant=variant, url=url)

        if method == 'association':
            name = request.POST.get('product')
            image_id = request.POST.get('image_id')
            database_product = get_object_or_404(models.Product, name__iexact=name)
            if database_product:
                image = self.queryset.get(id=int(image_id))
                database_product.images.add(image)
                return redirect('manage_images')

        return http.JsonResponse(data={'status': 'No image'})
        

    def get_context_data(self, **kwargs):
        queryset = super().get_queryset()
        context = super().get_context_data(**kwargs)

        # Pagination for VueJS
        paginator = Paginator(queryset, 8)
        page = self.request.GET.get('page')
        images = paginator.get_page(page)
        images = serializers.ImageSerializer(instance=images.object_list, many=True)
        context['vue_images'] = images.data
        context['product_form'] = forms.ImagesForm()
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

@login_required
def send_email(request, **kwargs):
    sender = None
    receiver = None
    message = None

    status = send_email(request, sender=sender, \
                receiver=receiver, message=message)

    return http.JsonResponse(data={})

class CouponsView(LoginRequiredMixin, generic.ListView):
    model = models.PromotionalCode
    queryset = models.PromotionalCode.objects.all()
    template_name = 'pages/lists/coupons.html'
    context_object_name = 'coupons'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        queryset = super().get_queryset()
        serialized_coupons = serializers.PromotionalCodeSerializer(queryset, many=True)
        context['vue_coupons'] = serialized_coupons.data
        return context

class CreateCouponsView(LoginRequiredMixin, generic.CreateView):
    model = models.PromotionalCode
    template_name = 'pages/create_coupons.html'
    context_object_name = 'coupon'
  

# CHARTS VIEWS

class BaseAPIView(APIView):
    authentication_classes = []
    permission_classes = []

class ChartsView(BaseAPIView):
    def get(self, format=None, **kwargs):
        payments_by_month = models.CustomerOrder\
                            .statistics.payments_by_month()
        # print(payments_by_month)
        data = {
            "myChart": {
                'labels': payments_by_month[0],
                # 'labels': ["Red", "Blue", "Yellow", "Green", "Purple", "Orange"]
                # 'data': [4, 5, 15, 34, 12, 98]
                'data': payments_by_month[1]
            }
        }
        return Response(data=data[kwargs['name']])
