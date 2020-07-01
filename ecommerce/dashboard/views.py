import csv
import io
import random
import re

from django import http
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core import exceptions
from django.core.mail import send_mail, send_mass_mail
from django.core.paginator import Paginator
from django.db.models.expressions import F, Q
from django.shortcuts import get_object_or_404, redirect, render, reverse
from django.utils.decorators import method_decorator
from django.views import generic
from django.views.decorators import http as views_decorators
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
            'carts_without_orders': models.Cart.statistics.carts_without_orders(),
            'orders_count': models.CustomerOrder.statistics.total_count(),
            'latest_orders': models.CustomerOrder.statistics.latest_orders(),
            'revenue': models.CustomerOrder.statistics.revenue(),
            'awaiting': models.CustomerOrder.statistics.awaiting_revenue(),
            'refunded': models.CustomerOrder.statistics.total_refunded_orders()
        }
        return render(request, 'pages/home.html', context)


# ############
#
# PRODUCTS
#
# ############

class ProductsView(LoginRequiredMixin, generic.ListView):
    model = models.Product
    queryset = models.Product.objects.all()
    template_name = 'pages/lists/products.html'
    context_object_name = 'products'
    paginate_by = 10

    def get(self, request, *args, **kwargs):
        get_request = super().get(request, *args, **kwargs)
        # This section resets the next_for_update in the
        # session to prevent persistence when trying to
        # return to the product page
        previous_searched_terms = self.request.session.get('next_for_update')
        if previous_searched_terms:
            self.request.session.pop('next_for_update')
        return get_request


class ProductView(LoginRequiredMixin, generic.DetailView):
    """The details of a specific product
    """
    model = models.Product
    queryset = models.Product.objects.all()
    template_name = 'pages/update/product.html'
    context_object_name = 'product'

    def post(self, request, **kwargs):
        method = request.POST.get('method')
        if not method:
            return http.JsonResponse(data={'status': 'Ok.'}, status=202)

        product = super().get_object()

        response_data = {'status': 'Done'}

        if method == "images":
            url_or_file = request.POST.get('type')
            if url_or_file == 'url':
                name = request.POST.get('name')
                url = request.POST.get('url')
                variant = request.POST.get('variant')
                main_image = request.POST.get('asmain')
                if main_image == 'true':
                    main_image = True
                else:
                    main_image = False
                if url.endswith('.jpg') \
                    or url.endswith('.webp') \
                        or url.endswith('.jpeg'):
                    if url is None:
                        url = 'https://mdbootstrap.com/img/Photos/Horizontal/E-commerce/Products/17.jpg'
                    image = models.Image.objects.create(name=name, url=url,
                                                        variant=variant, main_image=main_image)
                    product.images.add(image)
                else:
                    messages.error(
                        request, "L'URL doit être le lien vers une image de type JPEG/JPG/WEBP", extra_tags='alert-danger')
            else:
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
                images = product.images.all().exists()
                if not images:
                    response_data.update({'reload': True})
                    messages.success(request, f"Vous venez d'activer {product.name} \
                            et ce dernier ne possède aucune image", extra_tags='alert-warning')
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

        if method == "unlinkmainimage":
            try:
                # Encapsulated in a get function because
                # main image might return many values
                image = product.images.get(main_image=True)
            except exceptions.MultipleObjectsReturned:
                messages.error(
                    request, "Il semblerait qu'il y ait eu un problème avec les images", extra_tags='alert-danger')
            except:
                messages.error(request, "Une erreur s'est produite",
                               extra_tags='alert-danger')
            else:
                product.images.remove(image)
                messages.warning(
                    request, "Le produit ne possède plus d'image principale", extra_tags='alert-warning')

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
                product.images.clear()
                for image in database_images:
                    product.images.add(image)
            return redirect(reverse('dashboard_product', args=[product.id]))

        return http.JsonResponse(data=response_data)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        product = super().get_object()
        context['additional_images'] = product.images.filter(main_image=False)
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

    def post(self, request, **kwargs):
        user = super().get_object()
        try:
            user.email_user('subject', 'message',
                            from_email='contact.nawoka@gmail.com')
        except:
            messages.warning(
                request, "L'email n'a pas pu être envoyé", extra_tags='alert-warning')
        else:
            messages.success(
                request, f"Email envoyé à {user.email}", extra_tags='alert-success')
        return redirect(reverse('dashboard_user', args=[user.id]))


class SearchView(LoginRequiredMixin, generic.ListView):
    model = models.Product
    template_name = 'pages/lists/search/products.html'
    context_object_name = 'products'
    paginate_by = 10

    def get_context_data(self, **kwargs):
        context = super().get_context_data()
        context['search'] = searched_term = self.request.GET.get('s')
        self.request.session.update({'next_for_update': searched_term})

        # TODELETE: Not sure what this serves to
        context['extra_url_params'] = f"&s={searched_term}"
        return context

    def get_queryset(self):
        queryset = super().get_queryset()
        searched_item = self.request.GET.get('s')

        if ':' in searched_item:
            key, value = searched_item.split(':')
            if key == 'state':
                if value == 'actif' \
                    or value == 'true' \
                        or value == 'True':
                    return queryset.filter(active=True)
                elif value == 'inactif' \
                    or value == 'false' \
                        or value == 'False':
                    return queryset.filter(active=False)

        if searched_item.startswith('-'):
            searched_item = re.search(r'^-(?:\s?)(.*)', searched_item).group(1)
            terms = ~Q(name__icontains=searched_item) & ~Q(reference__icontains=searched_item) \
                & ~Q(collection__name__icontains=searched_item)
        else:
            terms = Q(name__icontains=searched_item) | Q(reference__icontains=searched_item) \
                | Q(collection__name__icontains=searched_item)

        return queryset.filter(terms)


class CustomerOrdersView(LoginRequiredMixin, generic.ListView):
    """All the orders made by customers for a specific company
    """
    model = models.CustomerOrder
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
    model = models.CustomerOrder
    context_object_name = 'orders'
    template_name = 'pages/lists/orders.html'

    def get_queryset(self):
        product = get_object_or_404(models.Product, id=self.kwargs['pk'])
        queryset = product.cart.product.all()
        return queryset


class CustomerOrderView(LoginRequiredMixin, generic.UpdateView):
    """Orders for one single product
    """
    model = models.CustomerOrder
    form_class = forms.CustomerOrderForm
    template_name = 'pages/update/order.html'
    context_object_name = 'order'

    def get_success_url(self):
        order = super().get_object()
        return reverse('customer_order', args=[order.id])


@login_required
@views_decorators.require_http_methods('POST')
def create_images(request, **kwargs):
    method = request.POST.get('method')

    if method == 'new':
        images = []
        data = request.POST.dict()

        for _, value in data.items():
            if value.endswith('.jpeg') or \
                    value.endswith('.jpg'):
                images.append(value)

        images_objects = []
        for index, url in enumerate(images):
            if index == 0:
                images_objects.append(models.Image(url=url, main_image=True))
            else:
                images_objects.append(models.Image(url=url))

        new_images = models.Image.objects.bulk_create(images_objects)
        request.session['images_to_associate'] = [
            image.id for image in new_images]
        return http.JsonResponse(data={'status': 'Uploaded'})

    if method == 'update':
        product_id = request.POST.get('product')
        product = get_object_or_404(models.Product, id=product_id)

    return http.JsonResponse(data={'status': 'Uploaded'})


@login_required
@views_decorators.require_POST
def preflight_images(request):
    """This is a preflight function that stores the
    urls of the images in the session before the create product
    form is submitted. This allows a two step creation process.
    """
    method = request.POST.get('method')
    if method != 'preflight-image-url':
        return http.JsonResponse(data={'state': False})

    url = request.POST.get('url')
    urls = request.session.get('images_urls')
    stream = io.StringIO()
    if urls:
        stream.write(urls + ', ' + url)
    else:
        stream.write(url)

    request.session.update({'images_urls': stream.getvalue()})

    stream.flush()
    stream.close()

    return http.JsonResponse(data={'state': True, 'url': url})


class CreateProductView(LoginRequiredMixin, generic.CreateView):
    model = models.Product
    queryset = models.Product.objects.all()
    form_class = forms.ProductForm
    template_name = 'pages/create/product.html'
    context_object_name = 'product'

    def get(self, request, *args, **kwargs):
        data = super().get(request, *args, **kwargs)
        request.session.update({'images_urls': ''})
        return data

    def post(self, request, *args, **kwargs):
        data = super().post(request, *args, **kwargs)

        images = request.session.get('images_urls')

        # TODO
        # if images:
        #     urls = images.split(',')

        #     database_images = []
        #     for index, url in enumerate(urls):
        #         n = random.randrange(1000, 9999)
        #         if index == 0:
        #             database_images.append(models.Image(name=f'NouvelImage{n}', url=url, main_image=True))
        #         database_images.append(models.Image(name=f'NouvelImage{n}', url=url))
        #     created_images = models.Image.objects.bulk_create(images)

        #     product = super().get_object()
        #     product.images.set(created_images)

        #     request.session.update({'images_urls': None})
        return data

    def get_success_url(self):
        return reverse('dashboard_products')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['post_to_view'] = reverse('dashboard_create')
        return context


class UpdateProductView(LoginRequiredMixin, generic.UpdateView):
    model = models.Product
    template_name = 'pages/update/product.html'
    form_class = forms.ProductForm
    context_object_name = 'product'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        product = super().get_object()
        context['post_to_view'] = reverse('update', args=[product.id])

        # If we clicked update from the search page,
        # this method allows to return that same
        # search page as opposed to all the products
        context['return_to_search'] = self.request.session.get(
            'next_for_update') or None

        queryset = super().get_queryset()
        queryset_list = list(queryset.values_list('id', flat=True))
        queryset_list_length = len(queryset_list)
        current_product_index = queryset_list.index(product.id)

        next_product_index = current_product_index + 1
        if next_product_index == queryset_list_length:
            next_product_index = 0
            context['disable_next'] = True

        context['previous_product'] = reverse(
            'update', args=[queryset_list[current_product_index - 1]])
        context['next_product'] = reverse(
            'update', args=[queryset_list[next_product_index]])
        return context

    def get_success_url(self):
        product = super().get_object()
        return reverse('update', args=[product.id])


class CartsView(LoginRequiredMixin, generic.ListView):
    model = models.Cart
    queryset = models.Cart.objects.all()
    template_name = 'pages/lists/carts.html'
    context_object_name = 'carts'
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
            main_image = request.POST.get('mainimage')
            image = self.model.objects.create(
                name=name, variant=variant, url=url)
            if main_image == "true":
                image.main_image = True
                image.save()

        if method == 'asmain':
            image_id = request.POST.get('image_id')
            image = self.model.objects.get(id=int(image_id))
            if image:
                if image.main_image:
                    image.main_image = False
                else:
                    image.main_image = True
                image.save()

        if method == 'association':
            name = request.POST.get('product')
            image_id = request.POST.get('image_id')
            database_product = get_object_or_404(
                models.Product, name__iexact=name)
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
        images = serializers.ImageSerializer(
            instance=images.object_list, many=True)
        context['vue_images'] = images.data
        # context['product_form'] = forms.ImagesForm()
        return context


class ImageView(LoginRequiredMixin, generic.DetailView):
    model = models.Image
    queryset = models.Image.objects.all()
    template_name = 'pages/details/image.html'
    context_object_name = 'image'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        image = super().get_object()

        initial_values = {'name': image.name, 'url': image.url}
        context['form'] = forms.ImageForm(initial=initial_values)

        # This section determines if the image
        # is linked to products and if so, display
        # these details to the user
        products = image.product_set.all()
        has_products = products.exists()
        context['is_linked'] = has_products
        if has_products:
            context['images_form'] = forms.ImageAssociationForm(
                initial={'products': [products.first().name]})
        else:
            context['images_form'] = forms.ImageAssociationForm()
        return context

    def post(self, request, **kwargs):
        method = request.POST.get('method')
        image = super().get_object()

        if method == 'details':
            form = forms.ImageForm(request.POST)
            if form.is_valid():
                image.name = form.cleaned_data['name']
                image.url = form.cleaned_data['url']
                image.save()
                messages.success(request, "L'image a été changé",
                                 extra_tags='alert-success')

        if method == 'associate':
            product_to_associate = request.POST.get('products')
            try:
                product = models.Product.objects.get(
                    name__iexact=product_to_associate)
            except exceptions.MultipleObjectsReturned:
                messages.success(
                    request, "Une erreur est survenue - Plusieurs produits ayant le même nom", extra_tags='alert-warning')
                return redirect(reverse('manage_image', args=[image.id]))
            image.product_set.clear()
            image.product_set.add(product)
            messages.success(
                request, f"Cette image a été associé à {product.name}", extra_tags='alert-success')

        if method == 'dissociate':
            if not image.product_set.all().exists():
                messages.warning(
                    request, f"Cette image n'était associé à aucun produit", extra_tags='alert-warning')
            else:
                image.product_set.clear()
                messages.success(
                    request, f"Cette image a été dissocié de tout produit", extra_tags='alert-success')

        return redirect(reverse('manage_image', args=[image.id]))


@login_required
def delete_view(request, **kwargs):
    method = kwargs['method']
    if method == 'products':
        item = get_object_or_404(models.Product, id=kwargs['pk'])

    if method == 'carts':
        item = get_object_or_404(models.Cart, id=kwargs['pk'])
        # Check if the cart has orders and if so,
        # mark them as terminated or completed
        item.customerorder_set.all().update(completed=True)

    item.delete()
    url = f'dashboard_{method}'
    messages.success(request, f"L'élément a été supprimé",
                     extra_tags='alert-success')

    page = request.GET.get('page')
    url = reverse(url)
    if page:
        url = url + f'?page={page}'
    return redirect(url)


@login_required
def delete_product_update_page(request, **kwargs):
    item = get_object_or_404(models.Product, id=kwargs['pk'])
    item.delete()
    messages.success(
        request, f"{item.name} a été supprimé", extra_tags='alert-success')
    return redirect('dashboard_products' or request.GET.get('next'))


@login_required
@views_decorators.require_http_methods('POST')
def duplicate_view(request, **kwargs):
    product = get_object_or_404(models.Product, id=kwargs['pk'])
    if not product:
        messages.error(
            request, "Le produit n'a pas pu être dupliqué", extra_tags="alert-warning")
        return redirect(reverse('update', args=[product.id]))
    base = {
        'name': f'Copie de {product.name}',
        'gender': product.gender,
        'description': product.description,
        'price_ht': product.price_ht,
        'slug': f'copie-de-{product.slug}',
        'collection': product.collection,
        'discount_pct': product.discount_pct,
    }
    try:
        new_product = models.Product.objects.create(**base)
    except:
        messages.error(
            request, "Le produit n'a pas pu être dupliqué", extra_tags='alert-warning')
        return http.JsonResponse(data={'state': False}, code=400)
    messages.success(
        request, f"{new_product.name} a bien été créer", extra_tags="alert-success")
    # return redirect(reverse('update', args=[new_product.id]))
    return http.JsonResponse(data={'redirect_url': reverse('update', args=[new_product.id])})


class Settings(LoginRequiredMixin, generic.View):
    def get(self, request, *args, **kwargs):
        return render(request, 'settings.html', {})


@login_required
def send_email(request, **kwargs):
    sender = None
    receiver = None
    message = None

    status = send_email(request, sender=sender,
                        receiver=receiver, message=message)

    return http.JsonResponse(data={})


# ############
#
# DISCOUNTS
#
# ############

class CouponsView(LoginRequiredMixin, generic.ListView):
    model = models.Discount
    queryset = models.Discount.objects.all()
    template_name = 'pages/lists/coupons.html'
    context_object_name = 'coupons'


class CreateCouponsView(LoginRequiredMixin, generic.CreateView):
    model = models.Discount
    form_class = forms.DiscountForm
    queryset = models.Discount.objects.all()
    template_name = 'pages/create/coupon.html'
    context_object_name = 'coupon'


class UpdateCouponsView(LoginRequiredMixin, generic.UpdateView):
    model = models.Discount
    form_class = forms.DiscountForm
    queryset = models.Discount.objects.all()
    template_name = 'pages/create/coupon.html'
    context_object_name = 'coupon'
    success_url = '/dashboard/coupons'


@login_required
@csrf_exempt
@views_decorators.require_http_methods('POST')
def upload_csv(request):
    file = request.FILES
    try:
        data = file['newcsvfile']
    except:
        messages.error(request, "Une erreur s'est produite",
                       extra_tags='alert-warning')
        return http.JsonResponse({'state': False})

    if not data.name.endswith('.csv'):
        messages.error(request, "Le fichier doit être de type .csv",
                       extra_tags='alert-warning')
        return http.JsonResponse({'state': False})

    try:
        csv_data = data.read().decode('UTF-8')
    except:
        messages.error(request, "Le fichier n'a pas pu être lu",
                       extra_tags='alert-warning')
        return http.JsonResponse({'state': False})
    else:
        data_stream = io.StringIO(csv_data)

        rows = list(csv.reader(data_stream, delimiter=',', quotechar="|"))
        headers = rows.pop(0)

        # Check that we have all the required
        # fields before uploading anythin to the
        # database and have consistent products
        required_keys = ['name', 'price_ht', 'gender', 'collection']
        missing_fields = [
            required_key for required_key in required_keys if required_key not in headers]
        if missing_fields:
            messages.error(
                request, f"Les champs suivants sont manquants: {', '.join(missing_fields)}", extra_tags='alert-warning')
            return http.JsonResponse({'state': False})

        try:
            products = []
            for row in rows:
                # Check that each row is factually
                # equals to the length of the header -;
                # raise and catch an exception if not
                # the case
                if len(row) != len(headers):
                    raise Exception(
                        "The header length is not equals to the row length")
                products.append(list(zip(headers, row)))
        except:
            messages.error(
                request, "L'entête ne correspond pas au nombre de produits", extra_tags='alert-error')
            return http.JsonResponse({'state': False})
        else:
            database_products = []
            collections = models.ProductCollection.objects.all()
            for item in products:
                for field in item:
                    key = field[0]
                    value = field[1]
                    if key == 'collection':
                        try:
                            value = collections.get(name__iexact=value)
                        except exceptions.ObjectDoesNotExist:
                            value = collections.first()
                            messages.error(
                                request, "La collection %s n'existe pas. Nous avons assigné les produits à une collection par défaut", extra_tags='alert-warning')
                    database_products.append(models.Product(**{key: value}))
            print(database_products)

    messages.error(request, "Les produits ont été créés",
                   extra_tags='alert-success')
    return http.JsonResponse(data={'state': True})


@login_required
@views_decorators.require_http_methods('GET')
def download_csv(request):
    method = request.GET.get('method')
    if not method or method == 'all':
        products = models.Product.product_manager.filter(active=True)
    elif method == 'current':
        pass
    elif method == 'collection':
        name = request.GET.get('using')
        if not name:
            pass
        else:
            try:
                products = models.ProductCollection\
                    .collection_manager.active_products(name)
            except:
                products = []

    rows = []
    response = http.HttpResponse(content_type='text/csv')

    csv_writer = csv.writer(response)
    csv_writer.writerow(['id', 'title', 'description', 'condition', 'availability',
                         'link', 'brand', 'price',
                         'image_link', 'google_product_category', 'gender',
                         'is_final_sale', 'return_policy_days', 'inventory'])
    for product in products:
        url = f'https://nawoka.fr{product.get_absolute_url()}'
        if product.gender == 'femme':
            gender = 'female'
        else:
            gender = 'male'
        rows.append(
            [
                product.id, product.name, product.description, 'new', 'in stock',
                url, 'Nawoka', product.get_price(),
                product.get_main_image_url, product.google_category, gender,
                False, 14, 50
            ]
        )
    csv_writer.writerows(rows)

    response['Content-Disposition'] = 'inline; filename=products.csv'
    return response


# ############
#
# COLLECTIONS
#
# ############

class CollectionsView(LoginRequiredMixin, generic.ListView):
    model = models.Collection
    queryset = models.Collection.objects.all()
    template_name = 'pages/lists/collections.html'
    context_object_name = 'collections'
    paginate_by = 10


class CreateCollectionView(LoginRequiredMixin, generic.CreateView):
    model = models.Collection
    form_class = forms.CollectionForm
    template_name = 'pages/create/collection.html'
    context_object_name = 'collection'


class UpdateCollectionView(LoginRequiredMixin, generic.UpdateView):
    model = models.Collection
    form_class = forms.CollectionForm
    template_name = 'pages/update/collection.html'
    context_object_name = 'collection'

    def get_success_url(self):
        product = super().get_object()
        return reverse('update_collection', args=[product.id])


# ############
#
# CUSTOMERS
#
# ############

class CreateCustomerView(LoginRequiredMixin, generic.CreateView):
    model = MYUSER
    form_class = forms.CustomerForm
    template_name = 'pages/create/customer.html'
    context_object_name = 'customer'


# ############
#
# PURCHASES
#
# ############

# class PurchaseOrderView(LoginRequiredMixin, generic.CreateView):
class PurchaseOrderView(LoginRequiredMixin, generic.TemplateView):
    template_name = 'pages/create/purchase_order.html'


# ############
#
# CHARTS
#
# ############

class BaseAPIView(APIView):
    authentication_classes = []
    permission_classes = []


class ChartsView(BaseAPIView):
    def get(self, format=None, **kwargs):
        payments_by_month = models.CustomerOrder\
            .statistics.payments_by_month()
        data = {
            "myChart": {
                'labels': payments_by_month[0],
                'data': payments_by_month[1]
            }
        }
        return Response(data=data[kwargs['name']])
