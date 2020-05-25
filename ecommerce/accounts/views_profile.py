import datetime
import re

from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import Http404, HttpResponseForbidden, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render, reverse
from django.utils.translation import gettext
from django.utils.translation import gettext_lazy as _
from django.views.generic import View

from accounts.forms import AddressProfileForm, BaseProfileForm
from accounts.models import MyUser, MyUserProfile


class ProfileView(LoginRequiredMixin, View):
    """Index page of the profile
    """
    def get(self, request, *args, **kwargs):
        user = get_object_or_404(MyUser, id=request.user.id)
        profile = user.myuserprofile_set.get(myuser=request.user.id)

        context = {
            'base_profile_form': BaseProfileForm(
                initial = {
                    'name': user.name,
                    'surname': user.surname
                }
            ),
            'address_profile_form': AddressProfileForm(
                initial = {
                    'address': profile.address,
                    'city': profile.city,
                    'zip_code': profile.zip_code
                }
            ),
            'forms': {
                'userform': {
                    'name': user.name,
                    'surname': user.surname
                }
            }
        }

        if 'vue' in request.GET:
            if request.GET.get('vue') == 'true':
                return render(request, 'pages/accounts/vue/profile.html', context)

        return render(request, 'pages/accounts/profile.html', context)

    def post(self, request, **kwargs):
        form = None
        user_id = request.user
        user = MyUser.objects.get(id=user_id.id)
        user_profile = user.myuserprofile_set.get(myuser=user_id.id)

        form_id = request.POST.get('form_id')

        if form_id == 'userform':
            form = BaseProfileForm(request.POST, instance=user)

        if form_id == 'detailsform':
            form = AddressProfileForm(request.POST, instance=user_profile)
            # VUE
            # data = self.correct_vue_post_data(request.POST)
            # MyUserProfile.objects.update(**data)

        if not form:
            return JsonResponse({'error': 'Form not identified'}, status=500)
        else:
            if form.is_valid():
                form.save()

        return JsonResponse({'success': 'success'}, status=200)
    
    def correct_vue_post_data(self, data):
        """Corrects the query dict in order to be saved correctly
        to the database"""
        data = data.dict()
        data.pop('form_id')
        data.pop('csrfmiddlewaretoken')
        return {key: value for key, value in data.items()}

class ProfileDataView(LoginRequiredMixin, View):
    """Help the user manage his data
    """
    def get(self, request, *args, **kwargs):
        current_user = self.request.user

        try:
            # Query the social_auth database and
            # get a set of connected accounts
            user = self.request.user.social_auth.get(uid=current_user.email)
            if user:
                context = {
                    'provider': user.provider
                }
        except:
            context = {}

        return render(request, 'pages/accounts/data.html', context)

class ProfileDeleteView(LoginRequiredMixin, View):
    """Help the user delete his account
    """
    def get(self, request, *args, **kwargs):
        user = get_object_or_404(MyUser, id=request.user.id)
        user.delete()
        return redirect('/')

class PaymentMethodsView(LoginRequiredMixin, View):
    """Allows the customer to update his/her payment method"""
    
    def get(self, request, *args, **kwargs):
        return render(request, 'pages/accounts/payment_methods.html', {})

    def post(self, request, *kwargs):
        try:
            import stripe
        except ImportError:
            raise Http404('An error has occured')
        else:
            # We can update the customer's cards here
            # using the stripe api
            params = {
                'source': 'source'
            }
            stripe.Customer.update(**params)
        finally:
            response = {
                'status': ''
            }
        return JsonResponse(response)

class ChangePasswordView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        context = {
            'form': PasswordChangeForm(request.user),
        }
        return render(request, 'pages/accounts/reset_password.html', context)

    def post(self, request, **kwargs):
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            # IMPORTANT: to allow the user to stay logged
            update_session_auth_hash(request, user)
        return redirect('/profile/')

# class PersonalisationView(LoginRequiredMixin, View):
#     def get(self, request, *args, **kwargs):
#         context = {
#             'user_profile':self.get_user_profile,
#             'form': PersonalizationProfileForm
#         }
#         return render(request, 'accounts/profile_personalisation.html', context)

#     def post(self, request, **kwargs):
#         user_profile = self.get_user_profile
#         redirect('personalisation')

#     @property
#     def get_user_profile(self):
#         return MyUserProfile.objects.get(myuser_id_id=self.request.user.id)
