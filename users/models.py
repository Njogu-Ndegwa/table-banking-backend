# from django.contrib.auth.models import AbstractBaseUser
# from django.db import models

# class CustomUser(AbstractBaseUser):
#     # Add your custom fields here
#     phone_number = models.CharField(max_length=20)
#     id_number = models.CharField(max_length=20)
#     full_name = models.CharField(max_length=255)

#     USERNAME_FIELD = "phone_number"

from django.db import models
from django.contrib.auth.models import BaseUserManager, AbstractBaseUser


class MyUserManager(BaseUserManager):
    def create_user(self, phone_number, id_number, full_name, password=None):
        """
        Creates and saves a User with the given phone number, id_number, full_name and password.
        """
        if not phone_number:
            raise ValueError("Users must have a phone_number")

        user = self.model(
            phone_number = phone_number,
            id_number=id_number,
            full_name=full_name
        )

        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, phone_number, id_number, full_name, password=None):
        """
        Creates and saves a superuser with the given email, date of
        birth and password.
        """
        user = self.create_user(
            phone_number,
            id_number,
            full_name,
            password=password,
        )
        user.is_admin = True
        user.save(using=self._db)
        return user


class CustomUser(AbstractBaseUser):
    phone_number = models.CharField(max_length=20, unique=True)
    id_number = models.CharField(max_length=20, unique=True)
    full_name = models.CharField(max_length=255)
    is_active = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=False)
    roles = models.ManyToManyField('Role', related_name='users')
    partner = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='members')

    objects = MyUserManager()

    USERNAME_FIELD = "phone_number"
    REQUIRED_FIELDS = ["id_number", "full_name"]

    def __str__(self):
        return self.phone_number

    def has_perm(self, perm, obj=None):
        "Does the user have a specific permission?"
        # Simplest possible answer: Yes, always
        return True

    def has_module_perms(self, app_label):
        "Does the user have permissions to view the app `app_label`?"
        # Simplest possible answer: Yes, always
        return True

    @property
    def is_staff(self):
        "Is the user a member of staff?"
        # Simplest possible answer: All admins are staff
        return self.is_admin
    

class Role(models.Model):
    name = models.CharField(max_length=50, unique=True)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name

