from django.contrib.auth.models import BaseUserManager, GroupManager
from django.utils.translation import gettext
from django.utils.translation import gettext_lazy as _


class MyUserManager(BaseUserManager):
    def create_user(self, email, name=None, surname=None, username=None, password=None):
        """Creates a basic user for your application"""
        if not email:
            raise ValueError('You must provide an email address.')

        email = self.normalize_email(email)
        user = self.model(email=email, name=name, surname=surname)
        
        user.set_password(password)
        user.save(using=self._db)

        return user

    def create_superuser(self, email, name=None, surname=None, password=None):
        """Creates a superuser"""
        user = self.create_user(email, name=name, surname=surname, password=password)

        user.admin = True
        user.staff = True
        user.save(using=self._db)
        
        return user

    # def create_user_enterprise(self, email, nom=None, prenom=None, password=None, enterprise=True):
    #     if not email:
    #         raise ValueError(_("L'addresse mail est obligatoire"))

    #     user = self.model(
    #         email=self.normalize_email(email),
    #         nom=nom,
    #         prenom=prenom,
    #     )

    #     user.candidat=candidat
    #     user.set_password(password)
    #     user.save(using=self._db)

    #     return user
