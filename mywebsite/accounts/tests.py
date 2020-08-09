# from django.contrib.auth.models import AnonymousUser, User
from django.test import RequestFactory, TestCase
# from django.test.client import Client

# from accounts.models import AccountsToken, MyUser, MyUserProfile

# from .views import LoginView, SignupView


# class LoginTest(TestCase):
#     def setUp(self):
#         self.factory = RequestFactory()
#         self.user = MyUser.objects.create_user(
#             email='test@gmail.com',
#             nom='Test',
#             prenom='TestPre',
#             password='touparet'
#         )

#     def user_exists(self):
#         self.assertIsNotNone(self.user.email, 'User is none existant')

#     def user_can_login(self):
#         # Access login page
#         request = self.factory.get('/login/')
#         response = LoginView().as_view()(request)
#         self.assertEqual(response.status_code, 200, 'Page was not accessed')

#         request.user = self.user

#         # User logged in
#         request = self.factory.post('/login/', {'email': 'test@gmail.com', 'password': 'touparet'})
#         response = LoginView().as_view()(request)
#         self.assertEqual(response.status_code, 200, 'Page was not accessed')
#         self.assertEqual(request.user.email, 'test@gmail.com', 'N\'a pas d\'email')

#     def user_can_signup(self):
#         request = self.factory.post('/signup/', {'email': 'test@gmail.com', \
#                                                     'password': 'touparet',\
#                                                     'nom': 'Test', 'prenom': 'TestRe'})
#         response = SignupView().as_view()(request)

#         self.assertEqual(response.status_code, 200, 'User could not signup')
#         # self.assertFalse(request.user.nom == 'Test', 'Le nom n\'est pas Test')
