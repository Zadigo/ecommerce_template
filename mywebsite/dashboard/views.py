import csv
import io
import json
import random
import re

from cart import models as cart_models
from discounts import models as discount_models
from django import http
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required, permission_required
from django.core.paginator import Paginator
from django.db import transaction as atomic_transactions
from django.shortcuts import get_object_or_404, redirect, render, reverse
from django.utils.decorators import method_decorator
from django.utils.translation import gettext_lazy as _
from django.views import generic
from django.views.decorators import http as views_decorators
from django.views.decorators.csrf import csrf_exempt
from shop import choices, models, serializers, utilities

from dashboard import forms
from dashboard import models as dashboard_models
from dashboard.mixins import GroupAuthorizationMixin

MYUSER = get_user_model()

class IndexView(GroupAuthorizationMixin, generic.View):
    authorized_except_for_groups = ['Customer']

    def get(self, request, *args, **kwargs):
        context = {
            'carts_without_orders': cart_models.Cart.statistics.carts_without_orders(),
            'orders_count': cart_models.CustomerOrder.statistics.total_count(),
            'latest_orders': cart_models.CustomerOrder.statistics.latest_orders(),
            'revenue': cart_models.CustomerOrder.statistics.total_refunded_orders()
        }
        return render(request, 'pages/home.html', context)


class ProductsView(GroupAuthorizationMixin, generic.ListView):
    authorized_except_for_groups = ['Customer']
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

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        paginator = Paginator(self.queryset, self.paginate_by)
        page = self.request.GET.get('page')
        products = paginator.get_page(page)
        
        serialized_products = serializers.SimpleProductSerializer(
                                    instance=products.object_list, many=True)
        context['on_current_page'] = serialized_products.data
        context['number_of_items'] = self.queryset.count()
        return context


class SearchView(GroupAuthorizationMixin, generic.ListView):
    authorized_except_for_groups = ['Customer']
    model = models.Product
    template_name = 'pages/lists/search/products.html'
    context_object_name = 'products'
    paginate_by = 10

    def get_context_data(self, **kwargs):
        context = super().get_context_data()
        context['search'] = searched_term = self.request.GET.get('s')
        self.request.session.update({'next_for_update': searched_term})
        return context

    def get_queryset(self):
        searched_terms = self.request.GET.get('s')
        return self.model.product_manager.advanced_search(searched_terms)


class CreateProductView(GroupAuthorizationMixin, generic.CreateView):
    authorized_except_for_groups = ['Customer']
    model = models.Product
    queryset = models.Product.objects.all()
    form_class = forms.CreateProductForm
    template_name = 'pages/edit/create/product.html'
    context_object_name = 'product'

    def get_success_url(self):
        return reverse('dashboard:products:home')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['post_to_view'] = reverse('dashboard:products:create')

        # This triggers the apparation or
        # not of certain features on the update
        # and creation page. For instance, unlinking
        # an image on the creation is not necessary
        context['vue_edit_mode'] = 'create'
        return context


class UpdateProductView(GroupAuthorizationMixin, generic.UpdateView):
    authorized_except_for_groups = ['Customer']
    model = models.Product
    template_name = 'pages/edit/update/product.html'
    form_class = forms.UpdateProductForm
    context_object_name = 'product'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        product = super().get_object()
        context['post_to_view'] = reverse('dashboard:products:update', args=[product.id])

        # If we clicked update from the search page,
        # this method allows to return that same
        # search page as opposed to all the products
        context['return_to_search'] = self.request.session.get('next_for_update') or None

        # This section allows the user
        # to navigate from product to
        # product in the updae page
        # <- and -> arrows
        queryset = super().get_queryset()
        queryset_list = list(queryset.values_list('id', flat=True))
        queryset_list_length = len(queryset_list)
        current_product_index = queryset_list.index(product.id)

        next_product_index = current_product_index + 1
        if next_product_index == queryset_list_length:
            next_product_index = 0
            context['disable_next'] = True

        context['previous_product'] = reverse('dashboard:products:update', args=[queryset_list[current_product_index - 1]])
        context['next_product'] = reverse('dashboard:products:update', args=[queryset_list[next_product_index]])

        serialized_product = serializers.ProductSerializer(instance=product)
        context['vue_product'] = serialized_product.data

        images = models.Image.objects.all()
        context['images'] = images = images.exclude(id__in=product.images.values_list('id'))
        serialized_other_images = serializers.ImageSerializer(images, many=True)
        context['vue_other_images'] = serialized_other_images.data

        # This triggers the apparation or
        # not of certain features on the update
        # and creation page. For instance, unlinking
        # an image on the creation is not necessary
        context['vue_edit_mode'] = 'update'
        context['vue_unlink_image_url'] = reverse('dashboard:products:unlink', args=[product.id])
        return context

    def get_success_url(self):
        product = super().get_object()
        return reverse('dashboard:products:update', args=[product.id])




class UsersView(GroupAuthorizationMixin, generic.ListView):
    authorized_except_for_groups = ['Customer']
    model = MYUSER
    queryset = MYUSER.objects.all()
    template_name = 'pages/lists/users.html'
    context_object_name = 'users'
    paginate_by = 10


class UserView(GroupAuthorizationMixin, generic.DetailView):
    authorized_except_for_groups = ['Customer']
    model = MYUSER
    queryset = MYUSER.objects.all()
    template_name = 'pages/edit/update/profile.html'
    context_object_name = 'user'

    def post(self, request, **kwargs):
        user = super().get_object()
        try:
            user.email_user('subject', 'message', from_email='contact.mywebsite@gmail.com')
        except:
            messages.warning(request, "L'email n'a pas pu être envoyé", extra_tags='alert-warning')
        else:
            messages.success(request, f"Email envoyé à {user.email}", extra_tags='alert-success')
        return redirect(reverse('dashboard_user', args=[user.id]))




class CustomerOrdersView(GroupAuthorizationMixin, generic.ListView):
    """Show all the orders made by customers
    """
    authorized_except_for_groups = ['Customer']
    model   = cart_models.CustomerOrder
    queryset = cart_models.CustomerOrder.objects.all()
    template_name = 'pages/lists/orders.html'
    context_object_name = 'orders'
    paginate_by = 10


class CustomerOrderView(GroupAuthorizationMixin, generic.UpdateView):
    """Orders for one single product
    """
    authorized_except_for_groups = ['Customer']
    model = cart_models.CustomerOrder
    form_class = forms.CustomerOrderForm
    template_name = 'pages/edit/update/order.html'
    context_object_name = 'order'

    def get_success_url(self):
        order = super().get_object()
        return reverse('dashboard:customer_order', args=[order.id])




class CartsView(GroupAuthorizationMixin, generic.ListView):
    authorized_except_for_groups = ['Customer']
    model = cart_models.Cart
    queryset = cart_models.Cart.objects.all()
    template_name = 'pages/lists/carts.html'
    context_object_name = 'carts'
    paginate_by = 5



class ImagesView(GroupAuthorizationMixin, generic.ListView):
    authorized_except_for_groups = ['Customer']
    model = models.Image
    queryset = models.Image.objects.all()
    template_name = 'pages/lists/images.html'
    context_object_name = 'images'
    paginate_by = 8

    @atomic_transactions.atomic
    def post(self, request, **kwargs):
        authorized_methods = [
            'from-url', 'from-local'
        ]

        method = request.POST.get('method')

        if not method:
            message = {
                'level': messages.ERROR,
                'message': _("Une erreur s'est produite - IMG-UP"),
                'extra_tags': 'alert-error'
            }
        else:
            if method in authorized_methods:
                name = request.POST.get('new-image-name')
                variant = request.POST.get('new-image-variant')

                if not name:
                    message = {
                        'level': messages.ERROR,
                        'message': _("Vous devez attribuer un nom à votre image - IMG-UP"),
                        'extra_tags': 'alert-error'
                    }
                else:
                    if method == 'from-url':
                        url = request.POST.get('new-image-link')
                        models.Image.objects.create(**{'name': name, 'url': url, 'variant': variant})
                        message = {
                            'level': messages.SUCCESS,
                            'message': _("Vos images ont été téléchargé"),
                            'extra_tags': 'alert-success'
                        }
                    elif method == 'from-local':
                        pass

        messages.add_message(request, **message)
        return redirect(reverse('dashboard:images:home'))

    def get_context_data(self, **kwargs):
        queryset = super().get_queryset()
        context = super().get_context_data(**kwargs)
        
        paginator = Paginator(queryset, self.paginate_by)
        page = self.request.GET.get('page')
        images = paginator.get_page(page)
        
        serialized_images = serializers.ImageSerializer(images.object_list, many=True)
        context['vue_images'] = serialized_images.data
        return context

@method_decorator(atomic_transactions.atomic, name='post')
class ImageView(GroupAuthorizationMixin, generic.UpdateView):
    authorized_except_for_groups = ['Customer']
    model = models.Image
    queryset = models.Image.objects.all()
    form_class = forms.ImageForm
    template_name = 'pages/edit/update/image.html'
    context_object_name = 'image'

    def get_success_url(self):
        image = super().get_object()
        return reverse('dashboard:images:update', args=[image.id])


class SettingsView(GroupAuthorizationMixin, generic.TemplateView):
    authorized_except_for_groups = ['Customer']
    template_name = 'pages/edit/update/settings/index.html'
    
    # def get_context_data(self, **kwargs):
    #     context = super().get_context_data(**kwargs)
    #     user = self.request.user
    #     try:
    #         user_store = dashboard_models.DashboardSetting.objects.get(user=self.request.user)
    #     except:
    #         user_has_store = False
    #     else:
    #         user_has_store = True
    #         context['store'] = user_store
    #     context['user_has_store'] = user_has_store
    #     return context


class DashboardSettingsMixin:
    def custom_post(self, request, redirect_url, form, **kwargs):
        form = form(request.POST)
        if form.errors:
            messages.error(request, f'Le formulaire possède des erreurs: {[error for error in form.errors.keys()]}', extra_tags='alert-danger')
        if form.is_valid():
            item = dashboard_models.DashboardSetting.objects.filter(id=request.user.id)
            item.update(**form.cleaned_data)
        return redirect(reverse(redirect_url))


class GeneralSettingsView(GroupAuthorizationMixin, generic.View):
    authorized_except_for_groups = ['Customer']
    def get(self, request, *args, **kwargs):
        user = request.user
        setting = dashboard_models.DashboardSetting.objects.get(myuser=user)
        context = {
            'store': dashboard_models.DashboardSetting.objects.get(myuser=user),
            'form': forms.DashboardSettingsForm(
                initial={
                    'name': setting.name,
                    'legal_name': setting.legal_name,
                    'telephone': setting.telephone,
                    'contact_email': setting.contact_email,
                    'customer_care_email': setting.customer_care_email,
                    'automatic_archives': setting.automatic_archive
                }
            )
        }
        return render(request, 'pages/edit/update/settings/general.html', context)

    def post(self, request, **kwargs):
        form = forms.DashboardSettingsForm(request.POST)
        if form.errors:
            messages.error(request, f'Le formulaire possède des erreurs: {[error for error in form.errors.keys()]}', extra_tags='alert-danger')
        if form.is_valid():
            item = dashboard_models.DashboardSetting.objects.filter(id=request.user.id)
            item.update(**form.cleaned_data)
        return redirect(reverse('dashboard:settings:general'))


class StoreSettingsView(GroupAuthorizationMixin, generic.UpdateView):
    authorized_except_for_groups = ['Customer']
    model = dashboard_models.DashboardSetting
    # form_class = forms.DashboardSettingsForm
    form_class = None
    success_url = '/dashboard/settings'
    context_object_name = 'store'
    template_name = 'pages/edit/update/settings/shop.html'


class AnalyticsSettingsView(GroupAuthorizationMixin, DashboardSettingsMixin, generic.View):
    authorized_except_for_groups = ['Customer']
    def get(self, request, *args, **kwargs):
        user = request.user
        setting = dashboard_models.DashboardSetting.objects.get(myuser=user)
        context = {
            'store': dashboard_models.DashboardSetting.objects.get(myuser=user),
            'form': forms.AnalyticsSettingsForm(
                initial={
                    'google_analytics': setting.google_analytics,
                    'google_tag_manager': setting.google_tag_manager,
                    'google_optimize': setting.google_optimize,
                    'google_ads': setting.google_ads,
                    'facebook_pixels': setting.facebook_pixels,
                    'mailchimp': setting.mailchimp
                }
            )
        }
        return render(request, 'pages/edit/update/settings/analytics.html', context)

    def post(self, request, **kwargs):
        return self.custom_post(request, 'dashboard:settings:analytics', forms.AnalyticsSettingsForm, **kwargs)





class CouponsView(GroupAuthorizationMixin, generic.ListView):
    authorized_except_for_groups = ['Customer']
    model = discount_models.Discount
    queryset = discount_models.Discount.objects.all()
    template_name = 'pages/lists/coupons.html'
    context_object_name = 'coupons'


class CreateCouponsView(GroupAuthorizationMixin, generic.CreateView):
    authorized_except_for_groups = ['Customer']
    model = discount_models.Discount
    form_class = forms.DiscountForm
    queryset = discount_models.Discount.objects.all()
    template_name = 'pages/edit/create/coupon.html'
    context_object_name = 'coupon'


class UpdateCouponsView(GroupAuthorizationMixin, generic.UpdateView):
    authorized_except_for_groups = ['Customer']
    model = discount_models.Discount
    form_class = forms.DiscountForm
    queryset = discount_models.Discount.objects.all()
    template_name = 'pages/edit/update/coupon.html'
    context_object_name = 'coupon'

    def get_success_url(self):
        coupon = super().get_object()
        return reverse('dashboard:coupons:update', args=[coupon.id])




class CollectionsView(GroupAuthorizationMixin, generic.ListView):
    authorized_except_for_groups = ['Customer']
    model = models.Collection
    queryset = models.Collection.objects.all()
    template_name = 'pages/lists/collections.html'
    context_object_name = 'collections'
    paginate_by = 10


class CreateCollectionView(GroupAuthorizationMixin, generic.CreateView):
    authorized_except_for_groups = ['Customer']
    model = models.Collection
    form_class = forms.CollectionForm
    template_name = 'pages/edit/create/collection.html'
    context_object_name = 'collection'
    success_url = '/dashboard/collections'


class UpdateCollectionView(GroupAuthorizationMixin, generic.UpdateView):
    authorized_except_for_groups = ['Customer']
    model = models.Collection
    form_class = forms.CollectionForm
    template_name = 'pages/edit/update/collection.html'
    context_object_name = 'collection'

    def get_success_url(self):
        product = super().get_object()
        return reverse('dashboard:collections:update', args=[product.id])

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        second_conditions = [
            {'id': i, 'name': condition[0]} 
                for i, condition in enumerate(choices.SecondConditionsChoices.choices)
        ]
        context['vue_second_conditions'] = second_conditions
        return context




class CreateCustomerView(GroupAuthorizationMixin, generic.CreateView):
    authorized_except_for_groups = ['Customer']
    model = MYUSER
    form_class = forms.CustomerForm
    template_name = 'pages/edit/create/customer.html'
    context_object_name = 'customer'


class PurchaseOrderView(GroupAuthorizationMixin, generic.TemplateView):
    authorized_except_for_groups = ['Customer']
    template_name = 'pages/edit/create/purchase_order.html'




@csrf_exempt
@login_required
@atomic_transactions.atomic
@views_decorators.require_GET
def activate_coupon(request, **kwargs):
    state = False
    coupon = cart_models.Discount.objects.get(id=kwargs['pk'])
    if coupon:
        if coupon.active:
            coupon.active = False
        else:   
            coupon.active = True

        coupon.save()
        state = True
        message = {
            'level': messages.SUCCESS,
            'message': "Le coupon a été activé",
            'extra_tags': 'alert-success'
        }
    else:
        message = {
            'level': messages.ERROR,
            'message': "Une erreur s'est produite - COUP-AC",
            'extra_tags': 'alert-danger'
        }
    messages.add_message(request, **message)
    return http.JsonResponse(data={'state': state})


@csrf_exempt
@login_required
@views_decorators.require_POST
def upload_csv(request):
    file = request.FILES
    try:
        data = file['newcsvfile']
    except:
        messages.error(request, "Une erreur s'est produite", extra_tags='alert-warning')
        return http.JsonResponse({'state': False})
    
    if not data.name.endswith('.csv'):
        messages.error(request, "Le fichier doit être de type .csv", extra_tags='alert-warning')
        return http.JsonResponse({'state': False})

    messages.error(request, "Les produits ont été créés", extra_tags='alert-success')
    return http.JsonResponse(data={'state': True})


@csrf_exempt
@login_required
@views_decorators.require_http_methods(['GET', 'POST'])
def download_csv(request):
    authorized_exports = ['current', 'all', 'collection']
    method = request.GET.get('method') or request.POST.get('method')
    if method not in authorized_exports \
            or not method:
        messages.error(request, "Action non reconnue - EXP-C1", extra_tags='alert-danger')
        return http.JsonResponse(data={'state': False, 'code': 'EXP-C1'}, code=200)

    authorized_exports_for = ['general', 'facebook']
    export_for = request.GET.get('export_for')
    if export_for not in authorized_exports_for:
        messages.error(request, "Action non reconnue - EXP-C2", extra_tags='alert-danger')
        return http.JsonResponse(data={'state': False, 'code': 'EXP-C2'}, code=200)

    facebook_headers = ['id', 'title', 'description', 'condition', 'availability',
                            'link', 'brand', 'price', 'image_link', 'google_product_category', 
                                'gender', 'is_final_sale', 'return_policy_days', 'inventory']

    general_headers = ['id', 'name', 'description', 'price_pre_tax', 'active']

    if request.GET:
        if method == 'all':
            products = models.Product.product_manager.filter(active=True)
        elif method == 'collection':
            name = request.GET.get('using')
            if not name:
                messages.error(request, "Collection non reconnue - EXP-C3", extra_tags='alert-warning')
                return http.JsonResponse(data={'state': False, 'code': 'EXP-C3'}, code=200)
            else:
                try:
                    products = models.ProductCollection.collection_manager.active_products(name)
                except:
                    messages.error(request, "Collection non reconnue - EXP-C3", extra_tags='alert-warning')
                    return http.JsonResponse(data={'state': False, 'code': 'EXP-C3'}, code=200)
    
    if request.POST:
        if method == "current":
            product_ids = request.POST.get('products')
            try:
                product_ids = product_ids.split(',')
            except:
                raise http.Http404()
            else:
                product_ids = [int(pk) for pk in product_ids]
                if len(product_ids) == 0:
                    raise http.Http404()
            products = models.Product.objects.filter(pk__in=product_ids)

    if products:
        if export_for == 'general':
            headers = general_headers
        if export_for == 'facebook':
            headers = facebook_headers

        rows = []
        response = http.HttpResponse(content_type='text/csv')

        csv_writer = csv.writer(response)
        csv_writer.writerow(headers)

        for product in products:
            if export_for == 'general':
                rows.append(
                    [
                        product.id,
                        product.name,
                        product.description,
                        product.price_pre_tax,
                        product.active
                    ]
                )

            if export_for == 'facebook':
                url = f'https://namywebsitewoka.fr{product.get_absolute_url()}'
                if product.gender == 'femme':
                    gender = 'female'
                else:
                    gender = 'male'
                rows.append(
                    [
                        product.id,
                        product.name,
                        product.description,
                        'new',
                        'in stock',
                        url,
                        'Nawoka',
                        product.get_price(),
                        product.get_main_image_url,
                        product.google_category,
                        gender,
                        False,
                        14,
                        50
                    ]
                )

        csv_writer.writerows(rows)
        response['Content-Disposition'] = 'inline; filename=products.csv'
        return response

    messages.error(request, "Les données n'ont pas pu être exportéù - EXP-CG", extra_tags='alert-warning')
    return http.JsonResponse(data={'state': 'Failed'}, code=200)


@login_required
@atomic_transactions.atomic
@views_decorators.require_POST
def table_actions(request, **kwargs):
    method = request.POST.get('method')
    if not method or method == 'not-selected':
        messages.error(request, "Actions non reconnue - TAB-AC", extra_tags='alert-danger')
        return redirect(request.GET.get('next') or 'dashboard:home')

    authorized_methods = [
        'activate', 'deactivate', 'duplicate', 'delete', 'archive'
    ]
    if method not in authorized_methods:
        messages.error(request, "Actions non reconnue - TAB-AC", extra_tags='alert-danger')
        return redirect(request.GET.get('next') or 'dashboard:home')

    keys = request.POST.getlist('key')
    if not keys:
        messages.error(request, "Aucun éléments n'a été sélectionnés", extra_tags='alert-warning')
        return redirect(request.GET.get('next') or 'dashboard:home')

    products = models.Product.objects.filter(id__in=keys)
    number_of_products = products.count()

    if not products.exists():
        messages.warning(request, "Aucun élément n'a été trouvé", extra_tags='alert-warning')
        return redirect(request.GET.get('next') or 'dashboard:home')
    
    if number_of_products > 1:
        message_text = '{prefix} éléments ont été {suffix}s'
    else:
        message_text = '{prefix} élément a été {suffix}'

    message = {
        'level': messages.SUCCESS,
        'extra_tags': 'alert-success'
    }
    if method == 'activate':
        non_active_products = products.filter(active=False)
        non_active_products.update(active=True)
        message['message'] = message_text.format(prefix=number_of_products, suffix='activé')

    if method == 'deactivate':
        active_products = products.filter(active=True)
        active_products.update(active=False)
        message['message'] = message_text.format(prefix=number_of_products, suffix='désactivé')

    if method == 'duplicate':
        new_items = [
            models.Product(
                name=f'Copie de {product.name}',
                active=False
            ) for product in products
        ]
        models.Product.objects.bulk_create(new_items)
        message['message'] = message_text.format(prefix=number_of_products, suffix='dupliqué')

    if method == 'delete':
        products.delete()
        message['message'] = message_text.format(prefix=number_of_products, suffix='supprimé')

    if method == 'archive':
        message['message'] = message_text.format(prefix=number_of_products, suffix='archivé')

    messages.add_message(request, **message)
    return redirect(request.GET.get('next') or 'dashboard:home')


@login_required
@atomic_transactions.atomic
@views_decorators.require_GET
def delete_item_via_table(request, **kwargs):
    """
    Delete an element from the database via a table
    """
    method = kwargs['method']

    if method == 'products':
        item = get_object_or_404(models.Product, id=kwargs['pk'])

    if method == 'carts':
        item = get_object_or_404(cart_models.Cart, id=kwargs['pk'])
        # Check if the cart has orders and if so,
        # mark them as terminated or completed
        item.customerorder_set.all().update(completed=True)

    item.delete()

    url = f'dashboard:{method}:home'

    if method == 'carts':
        url = f'dashboard:carts'

    page = request.GET.get('page')
    url = reverse(url)
    if page:
        url = f'{url}?page={page}'

    messages.success(request, f"L'élément a été supprimé", extra_tags='alert-success')
    return redirect(url)


@login_required
@atomic_transactions.atomic
@views_decorators.require_GET
def delete_product(request, **kwargs):
    """
    Delete a product from the update page
    """
    item = get_object_or_404(models.Product, id=kwargs['pk'])
    item.delete()
    messages.success(
        request, f"{item.name} a été supprimé", extra_tags='alert-success')
    return redirect('dashboard:products:home' or request.GET.get('next'))


@login_required
@views_decorators.require_POST
def duplicate_view(request, **kwargs):
    state = False
    try:
        product = models.Product.objects.get(id=kwargs['pk'])
    except:
        messages.error(
            request, "Le produit n'a pas pu être dupliqué - DUP-NE", extra_tags='alert-danger')
        return http.JsonResponse(data={'state': state}, code=400)

    base = {
        'name': f'Copie de {product.name}',
        'gender': product.gender,
        'description': product.description,
        'price_pre_tax': product.price_pre_tax,
        'quantity': product.quantity,
        'slug': f'copie-de-{product.slug}',
        'collection': product.collection,
        'discount_pct': product.discount_pct,
        'discounted': product.discounted,
        'private': product.private
    }

    try:
        with atomic_transactions.atomic():
            new_product = models.Product.objects.create(**base)
    except:
        messages.error(
            request, "Le produit n'a pas pu être dupliqué - DUP-NP", extra_tags='alert-warning')
        return http.JsonResponse(data={'state': state}, code=400)
    else:
        # Also associate all images with the preceeding
        # product with the new one
        product_images = product.images.all()
        if product_images.exists():
            new_product.images.set(product_images)

    messages.success(
        request, f"{new_product.name} a été créer", extra_tags="alert-success")
    return http.JsonResponse(data={'redirect_url': reverse('dashboard:products:update', args=[new_product.id])})


@login_required
@views_decorators.require_POST
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
@csrf_exempt
@views_decorators.require_POST
def associate_images(request, **kwargs):
    product = models.Product.objects.get(id=kwargs['pk'])
    images = request.POST.get('image')
    if images:
        error = False
        for key in images:
            if not isinstance(key, int):
                error = True

        if error:
            messages.error(
                request, "Les images n'ont pas pu être associé - ASSO-ID", extra_tags='alert-warning')
            return http.JsonResponse(data={'state': False, })

        db_images = models.Image.objects.filter(id__in=images)
        product.images.set(db_images)

    messages.error(
        request, "Les images n'ont pas pu être associé - ASSO-ID", extra_tags='alert-warning')
    return http.JsonResponse(data={'state': False, })


@csrf_exempt
@atomic_transactions.atomic
@views_decorators.require_POST
def unlink_image_on_product_page(request, **kwargs):
    state = False
    product_id = kwargs['pk']
    image = request.POST.get('image')
    editmode = request.POST.get('method')
    
    editmodes = ['create', 'update']
    if not editmode or editmode not in editmodes:
        return http.JsonResponse(data={'state': False})
    
    if not image:
        messages.error(request, _("Une erreur s'est produite - IMG-UN"))
        return http.JsonResponse(data={'state': state})

    product = models.Product.objects.get(id=product_id)
    image = models.Image.objects.get(id=image)
    product.images.remove(image)
    return http.JsonResponse(data={'state': state})
