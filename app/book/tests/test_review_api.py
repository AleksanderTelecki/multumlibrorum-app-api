"""
Tests for the reviews API.
"""
from datetime import date
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import TestCase

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Review, Book

from book.serializers import ReviewDetailSerializer

REVIEW_URL = reverse('book:review-list')


def detail_url(review_id):
    return reverse('book:review-detail', args=[review_id])


def sample_user(email='test@londonappdev.com', password='testpass'):
    """Create a sample user"""
    return get_user_model().objects.create_user(email, password)


def sample_book(**params):
    """Create and return a sample book."""

    defaults = {
        'title': 'Sample book title',
        'isbn13': '978-3-16-148410-0',
        'publication_date': date(2022, 5, 7),
        'available_quantity': 25,
        'price': Decimal('5.50'),
        'description': 'Sample Book description'
    }

    defaults.update(params)

    book = Book.objects.create(**defaults)
    return book


def sample_review(user, book, comment='Sample Comment.', value=0):
    """Create and return a sample review."""

    if not user:
        user = sample_user()

    if not book:
        book = sample_book()

    review = Review.objects.create(
            user=user,
            book=book,
            comment='Test comment',
            value=4
    )

    return review


class PublicReviewsApiTests(TestCase):
    """Test api reviews request."""

    def setUp(self):
        self.client = APIClient()

    def test_retrieve_reviews(self):
        """Test list of reviews."""

        user = sample_user()
        book = sample_book()
        book1 = sample_book(title='New Sample Book')

        Review.objects.create(
            user=user,
            book=book,
            comment='Test comment',
            value=4
        )

        Review.objects.create(
            user=user,
            book=book1,
            comment='Test comment',
            value=3
        )

        res = self.client.get(REVIEW_URL)

        reviews = Review.objects.all().order_by('-book__title')
        serializer = ReviewDetailSerializer(reviews, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)


class PrivateReviewsApiTests(TestCase):
    """Test reviews requests for authorized user."""

    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            'test@example.com',
            'testpass123',
        )
        self.client.force_authenticate(self.user)

    def test_reviews_patch(self):
        """Test review update."""

        book = sample_book()
        review = sample_review(self.user, book)

        payload = {
            'book': book.id,
            'comment': 'Sample Comment.',
            'value': 4
        }

        url = detail_url(review.id)
        res = self.client.patch(url, payload)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        review.refresh_from_db()
        self.assertEqual(review.comment, payload['comment'])

    def test_reviews_put(self):
        """Test review update."""
        user = sample_user()
        book = sample_book()

        review = Review.objects.create(
            user=user,
            book=book,
            comment='Test comment',
            value=4
        )

        payload = {
            'book': book.id,
            'comment': 'New Sample Comment.',
            'value': 3
        }

        url = detail_url(review.id)
        res = self.client.put(url, payload)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        review.refresh_from_db()
        self.assertEqual(review.comment, payload['comment'])

    def test_reviews_delete(self):
        """Test deleting a reviews."""
        user = sample_user()
        book = sample_book()

        review = Review.objects.create(
            user=user,
            book=book,
            comment='Test comment',
            value=4
        )

        url = detail_url(review.id)
        res = self.client.delete(url)

        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        reviews = Review.objects.all()
        self.assertFalse(reviews.exists())
