from django.conf.urls import include, url
from django.contrib import admin
from django.urls import path, re_path
from django.views.generic import TemplateView

from accounts import views, views_profile

app_name = 'accounts'

profile_patterns = [
    url(r'^profile/payment-methods/$', views_profile.PaymentMethodsView.as_view(), name='payment_methods'),
    url(r'^profile/delete/$', views_profile.ProfileDeleteView.as_view(), name='delete_account'),
    url(r'^profile/data/$', views_profile.ProfileDataView.as_view(), name='profile_data'),
    url(r'^profile/change-password/$', views_profile.ChangePasswordView.as_view(), name='change_password'),
    url(r'^profile/$', views_profile.ProfileView.as_view(), name='profile'),
]

urlpatterns = [
    path('profile/', include(profile_patterns)),

    # url(r'^oauth/', include('social_django.urls', namespace='social')),
    
    url(r'^forgot-password/confirm/(?P<uidb64>[A-Z]+)/(?P<token>\w+\-\w+)$',
            views.UnauthenticatedPasswordResetView.as_view(), name='password_reset_confirm'),
    url(r'^forgot-password/$', views.ForgotPasswordView.as_view(), name='forgot_password'),
    url(r'^login/$', views.LoginView.as_view(), name='login'),
    url(r'^logout/$', views.LogoutView.as_view(), name='logout'),
    url(r'^signup/$', views.SignupView.as_view(), name='signup'),
    
]
