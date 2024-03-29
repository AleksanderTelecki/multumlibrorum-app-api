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

    def test_create_review(self):
        """Test creating a review is successful."""

        user = get_user_model().objects.create_user(
            'test@example.com',
            'testpass123'
        )
        book = models.Book.objects.create(
            title='Test Book',
            isbn13='978-3-16-148410-0',
            publication_date=datetime(2022, 5, 7),
            available_quantity=25,
            price=Decimal('5.50'),
            description='Sample Book description',
        )

        review = models.Review.objects.create(
            user=user,
            book=book,
            comment='Test comment',
            value=4
        )

        review.refresh_from_db()

        self.assertEqual(
            str(review),
            f"{str(review.book)} | {str(review.user)} | {review.value}"
        )

    def test_review_signal_create(self):
        """Test review create signal."""
        user = get_user_model().objects.create_user(
            'test@example.com',
            'testpass123'
        )
        user2 = get_user_model().objects.create_user(
            'test2@example.com',
            'testpass143'
        )
        book = models.Book.objects.create(
            title='Test Book',
            isbn13='978-3-16-148410-0',
            publication_date=datetime(2022, 5, 7),
            available_quantity=25,
            price=Decimal('5.50'),
            description='Sample Book description',
        )

        review1 = models.Review.objects.create(
            user=user,
            book=book,
            comment='Test comment',
            value=4
        )

        review2 = models.Review.objects.create(
            user=user2,
            book=book,
            comment='Test comment',
            value=3
        )

        avg = (review1.value+review2.value)/2

        book.refresh_from_db()

        self.assertEqual(book.rating, avg)

    def test_review_signal_delete(self):
        """Test review delete signal."""
        user = get_user_model().objects.create_user(
            'test@example.com',
            'testpass123'
        )
        user2 = get_user_model().objects.create_user(
            'test2@example.com',
            'testpass143'
        )
        book = models.Book.objects.create(
            title='Test Book',
            isbn13='978-3-16-148410-0',
            publication_date=datetime(2022, 5, 7),
            available_quantity=25,
            price=Decimal('5.50'),
            description='Sample Book description',
        )

        review1 = models.Review.objects.create(
            user=user,
            book=book,
            comment='Test comment',
            value=4
        )

        review2 = models.Review.objects.create(
            user=user2,
            book=book,
            comment='Test comment',
            value=3
        )

        review2.delete()

        avg = review1.value

        book.refresh_from_db()
        self.assertEqual(book.rating, avg)

        review1.delete()
        book.refresh_from_db()
        self.assertEqual(book.rating, 0)

    def test_create_orderitem(self):
        """Test creating a orderitem is successful."""

        user = get_user_model().objects.create_user(
            'test@example.com',
            'testpass123'
        )
        book = models.Book.objects.create(
            title='Test Book',
            isbn13='978-3-16-148410-0',
            publication_date=datetime(2022, 5, 7),
            available_quantity=25,
            price=Decimal('5.50'),
            description='Sample Book description',
        )

        orderitem = models.OrderItem.objects.create(
            user=user,
            book=book,
            quantity=2
        )

        orderitem.refresh_from_db()

        self.assertEqual(
            str(orderitem),
            (f"Book: {str(orderitem.book)} | "
                f"Quantity: {orderitem.quantity} | {orderitem.book.price}")
        )

    def test_create_likeditem(self):
        """Test creating a likeditem is successful."""

        user = get_user_model().objects.create_user(
            'test@example.com',
            'testpass123'
        )
        book = models.Book.objects.create(
            title='Test Book',
            isbn13='978-3-16-148410-0',
            publication_date=datetime(2022, 5, 7),
            available_quantity=25,
            price=Decimal('5.50'),
            description='Sample Book description',
        )

        likeditem = models.LikedItem.objects.create(
            user=user,
            book=book
        )

        likeditem.refresh_from_db()

        self.assertEqual(
            str(likeditem),
            f"Book: {str(likeditem.book)} | {likeditem.book.price}"
        )

    def test_create_ownedbook(self):
        """Test creating a ownedbook is successful."""

        user = get_user_model().objects.create_user(
            'test@example.com',
            'testpass123'
        )
        book = models.Book.objects.create(
            title='Test Book',
            isbn13='978-3-16-148410-0',
            publication_date=datetime(2022, 5, 7),
            available_quantity=25,
            price=Decimal('5.50'),
            description='Sample Book description',
        )

        ownedbook = models.OwnedBook.objects.create(
            user=user,
            book=book
        )

        ownedbook.refresh_from_db()

        self.assertEqual(
            str(ownedbook),
            f"Book: {str(ownedbook.book)}"
        )

    def test_create_order(self):
        """Test creating a order is successful."""
        user = get_user_model().objects.create_user(
            'test@example.com',
            'testpass123'
        )
        book = models.Book.objects.create(
            title='Test Book',
            isbn13='978-3-16-148410-0',
            publication_date=datetime(2022, 5, 7),
            available_quantity=25,
            price=Decimal('5.50'),
            description='Sample Book description',
        )

        book1 = models.Book.objects.create(
            title='Test Book 2',
            isbn13='978-3-16-148410-1',
            publication_date=datetime(2022, 5, 5),
            available_quantity=22,
            price=Decimal('5.60'),
            description='Sample Book description 2',
        )

        orderitem = models.OrderItem.objects.create(
            user=user,
            book=book,
            quantity=2
        )

        orderitem1 = models.OrderItem.objects.create(
            user=user,
            book=book1,
            quantity=1
        )

        order = models.Order.objects.create(
            user=user,
            paid_at=None,
            is_paid=False,
            is_digital=True
        )

        order.ordered_items.add(orderitem)
        order.ordered_items.add(orderitem1)

        sum = Decimal('0.0')
        for ordereditem in order.ordered_items.all():
            sum += (ordereditem.book.price * ordereditem.quantity)

        self.assertEqual(
            str(order),
            f"Count: {str(order.ordered_items.count())} | Total Price: {sum}"
        )
