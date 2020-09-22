from django.contrib.auth.models import BaseUserManager
from django.utils.translation import gettext
from django.utils.translation import gettext_lazy as _


class MyUserManager(BaseUserManager):
    def create_user(self, email, firstname=None, lastname=None, username=None, password=None):
        if not email:
            raise ValueError("Une addresse email est obligatoire")

        email = self.normalize_email(email)
        user = self.model(email=email, firstname=firstname, lastname=lastname)
        
        user.set_password(password)
        user.save(using=self._db)
        
        return user

    def create_superuser(self, email, firstname=None, lastname=None, password=None):
        user = self.create_user(email, firstname=firstname, lastname=lastname, password=password)

        user.is_admin = True
        user.is_staff = True
        user.save(using=self._db)
        
        return user

    def create_product_manager(self, email, firstname=None, lastname=None, password=None):
        user = self.create_user(email, firstname=firstname, lastname=lastname, password=password)

        user.product_manager = True
        user.staff = True
        user.save(using=self._db)

        return user
