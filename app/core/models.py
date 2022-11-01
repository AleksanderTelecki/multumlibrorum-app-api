"""
Database models.
"""

from django.db import models
from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager,
    PermissionsMixin,
)
from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator

from django.dispatch import receiver
from django.db.models.signals import post_save, post_delete
from django.db.models import Avg


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


class Publisher(models.Model):
    """Publishers for book."""
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name


class BookShelf(models.Model):
    """Bookshelfs for book."""
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name


class Language(models.Model):
    """Languages for book."""
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name


class Author(models.Model):
    """Authors for book."""
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name


class Genre(models.Model):
    """Genres for book."""
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name


class Book(models.Model):
    """Book object."""
    title = models.CharField(max_length=255)
    isbn13 = models.CharField(max_length=17)
    publication_date = models.DateField(blank=True, null=True)
    available_quantity = models.IntegerField(default=0)
    price = models.DecimalField(max_digits=5, decimal_places=2)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    genres = models.ManyToManyField(Genre)
    authors = models.ManyToManyField(Author)
    languages = models.ManyToManyField(Language)
    bookshelves = models.ManyToManyField(BookShelf)
    publishers = models.ManyToManyField(Publisher)
    rating = models.DecimalField(max_digits=2, decimal_places=1, default=0.0)

    def __str__(self):
        return self.title


class Review(models.Model):
    """Review object for book."""
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    comment = models.TextField(blank=True)
    value = models.IntegerField(
        default=1,
        validators=[
            MaxValueValidator(5),
            MinValueValidator(0)
        ]
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{str(self.book)} | {str(self.user)} | {self.value}"

    class Meta:
        # user can't have more than one review to one book
        unique_together = (("user", "book"),)


@receiver(post_save, sender=Review)
def review_created_handler(sender, instance, created, *args, **kwargs):
    """Handle create review event to recalculate book rating"""
    if created:
        book = Book.objects.get(id=instance.book.id)
        if Review.objects.filter(book=instance.book):
            book.rating = Review.objects.filter(book=instance.book) \
                .aggregate(Avg('value'))['value__avg']
            book.save()
        else:
            book.rating = 0
            book.save()


@receiver(post_delete, sender=Review)
def review_deleted_handler(sender, instance, *args, **kwargs):
    """Handle create review event to recalculate book rating"""
    book = Book.objects.get(id=instance.book.id)
    if Review.objects.filter(book=instance.book):
        book.rating = Review.objects.filter(book=instance.book) \
            .aggregate(Avg('value'))['value__avg']
        book.save()
    else:
        book.rating = 0
        book.save()
