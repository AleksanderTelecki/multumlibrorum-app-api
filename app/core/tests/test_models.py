"""
Tests for models.
"""
from datetime import datetime
from decimal import Decimal

from django.test import TestCase
from django.contrib.auth import get_user_model

from core import models


class ModelTests(TestCase):
    """Test models."""

    def test_create_user_with_email_successful(self):
        """Test creating a user with an email is successful."""
        email = 'test@example.com'
        password = 'testpass123'
        user = get_user_model().objects.create_user(
            email=email,
            password=password,
        )

        self.assertEqual(user.email, email)
        self.assertTrue(user.check_password(password))

    def test_new_user_email_normalized(self):
        """Test email is normilized for new users."""
        sample_emails = [
            ['test1@EXAMPLE.com', 'test1@example.com'],
            ['Test2@Example.com', 'Test2@example.com'],
            ['TEST3@EXAMPLE.COM', 'TEST3@example.com'],
            ['test4@example.COM', 'test4@example.com'],
        ]

        for email, expected in sample_emails:
            user = get_user_model().objects.create_user(email, 'testpass123')
            self.assertEqual(user.email, expected)

    def test_new_user_without_email_raises_error(self):
        """Test that creating user without an email raises a ValueError"""
        with self.assertRaises(ValueError):
            get_user_model().objects.create_user('', 'testpass123')

    def test_create_superuser(self):
        """Test creating a superuser"""
        user = get_user_model().objects.create_superuser(
            'test@example.com',
            'testpass123',
            )

        self.assertTrue(user.is_superuser)
        self.assertTrue(user.is_staff)

    def test_create_book(self):
        """Test creating a book is successful."""

        book = models.Book.objects.create(
            title='Test Book',
            isbn13='978-3-16-148410-0',
            publication_date=datetime(2022, 5, 7),
            available_quantity=25,
            price=Decimal('5.50'),
            description='Sample Book description',
        )

        self.assertEqual(str(book), book.title)

    def test_create_genre(self):
        """Test creating a genre is successful."""

        genre = models.Genre.objects.create(name='Test', description='Test')

        self.assertEqual(str(genre), genre.name)

    def test_create_author(self):
        """Test creating a author is successful."""

        author = models.Author.objects.create(name='Author Test')

        self.assertEqual(str(author), author.name)

    def test_create_language(self):
        """Test creating a language is successful."""

        language = models.Language.objects.create(name='English')

        self.assertEqual(str(language), language.name)

    def test_create_bookshelf(self):
        """Test creating a bookshelf is successful."""

        bookshelf = models.BookShelf.objects.create(
            name='Drakula',
            description='Bloody story.'
        )

        self.assertEqual(str(bookshelf), bookshelf.name)

    def test_create_publisher(self):
        """Test creating a bookshelf is successful."""

        publisher = models.Publisher.objects.create(
            name='New Publisher',
            description='Publisher description.'
        )

        self.assertEqual(str(publisher), publisher.name)
