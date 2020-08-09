from django.contrib.auth.models import BaseUserManager, GroupManager
from django.utils.translation import gettext
from django.utils.translation import gettext_lazy as _


class MyUserManager(BaseUserManager):
    def create_user(self, email, name=None, surname=None, username=None, password=None):
        if not email:
            raise ValueError("Une addresse email est obligatoire")

        email = self.normalize_email(email)
        user = self.model(email=email, name=name, surname=surname)
        
        user.set_password(password)
        user.save(using=self._db)
        
        return user

    def create_superuser(self, email, name=None, surname=None, password=None):
        user = self.create_user(email, name=name, surname=surname, password=password)

        user.is_admin = True
        user.is_staff = True
        user.save(using=self._db)
        
        return user

    def create_product_manager(self, email, name=None, surname=None, password=None):
        user = self.create_user(email, name=name, surname=surname, password=password)

        user.product_manager = True
        user.staff = True
        user.save(using=self._db)

        return user
