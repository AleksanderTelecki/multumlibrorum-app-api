"""
Database models.
"""

from django.conf import settings
from django.db import models # noqa
from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager,
    PermissionsMixin,
)


class UserManager(BaseUserManager):
    """Manager for users."""

    def create_user(self, email, password=None, **extra_fields):
        """Create, save and return a new user."""
        if not email:
            raise ValueError('User must have an email address.')
        user = self.model(email=self.normalize_email(email), **extra_fields)
        user.set_password(password)
        user.save(using=self._db)

        return user

    def create_superuser(self, email, password=None, **extra_fields):
        """Create, save and return a new superuser."""
        if not email:
            raise ValueError('User must have an email address.')
        superuser = self.model(
            email=self.normalize_email(email),
            **extra_fields,
        )
        superuser.is_staff = True
        superuser.is_superuser = True
        superuser.set_password(password)
        superuser.save(using=self._db)

        return superuser


class User(AbstractBaseUser, PermissionsMixin):
    """User in the system."""
    email = models.EmailField(max_length=255, unique=True)
    name = models.CharField(max_length=255)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    objects = UserManager()

    USERNAME_FIELD = 'email'


class Book(models.Model):
    """Book object."""
    title = models.CharField(max_length=255)
    isbn13 = models.CharField(max_length=17)
    publicationDate = models.DateField(blank=True, null=True)
    availableQuantity = models.IntegerField(default=0)
    price = models.DecimalField(max_digits=5, decimal_places=2)
    description = models.TextField(blank=True)
    createdAt = models.DateTimeField(auto_now_add=True)


    def __str__(self):
        return self.title 




