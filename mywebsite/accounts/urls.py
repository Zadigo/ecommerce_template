from django.conf.urls import include, url
from django.urls import path

from accounts import views, views_profile

app_name = 'accounts'

passwordpatterns = [
    url(r'^forgot-password/confirm/(?P<uidb64>[A-Z]+)/(?P<token>\w+\-\w+)$',
                views.UnauthenticatedPasswordResetView.as_view(), name='reset'),
    url(r'^forgot-password$', views.ForgotPasswordView.as_view(), name='forgot')
]

profilepatterns = [
    url(r'^change-password$', views_profile.ChangePasswordView.as_view(), name='change_password'),
    url(r'^contact-preferences$', views_profile.ContactPreferencesView.as_view(), name='contact'),
    url(r'^payment-methods$', views_profile.PaymentMethodsView.as_view(), name='payment'),
    url(r'^delete$', views_profile.ProfileDeleteView.as_view(), name='delete'),
    url(r'^data$', views_profile.ProfileDataView.as_view(), name='data'),
    url(r'^information$', views_profile.InformationView.as_view(), name='information'),
    url(r'^$', views_profile.IndexView.as_view(), name='home'),
]

urlpatterns = [
    path('profile/', include((profilepatterns, app_name), namespace='profile')),
    path('password/', include((passwordpatterns, app_name), namespace='password')),

    # url(r'^oauth/', include('social_django.urls', namespace='social')),

    url(r'^login$', views.LoginView.as_view(), name='login'),
    url(r'^logout$', views.LogoutView.as_view(), name='logout'),
    url(r'^signup$', views.SignupView.as_view(), name='signup'),
]
