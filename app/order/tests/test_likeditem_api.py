"""
Tests for the likeditem API.
"""
from datetime import date
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import TestCase

from rest_framework import status
from rest_framework.test import APIClient

from core.models import LikedItem, Book

from order.serializers import LikedItemDetailSerializer

LIKEDITEM_URL = reverse('order:likeditem-list')


def detail_url(likeditem_id):
    return reverse('order:likeditem-detail', args=[likeditem_id])


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


class PrivateLikedItemsApiTests(TestCase):
    """Test likeditems requests for authorized user."""

    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            'test@example.com',
            'testpass123',
        )
        self.client.force_authenticate(self.user)

    def test_retrieve_likeditems(self):
        """Test list of likeditems."""

        user = sample_user()
        book = sample_book()

        self.client.force_authenticate(user)

        LikedItem.objects.create(
            user=user,
            book=book
        )

        res = self.client.get(LIKEDITEM_URL)

        likeditems = LikedItem.objects.all().filter(user=user) \
            .order_by('-book__title')
        serializer = LikedItemDetailSerializer(likeditems, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_create_likeditem(self):
        """Test adding an likeditem to cart."""
        user = sample_user()
        self.client.force_authenticate(user)
        book = sample_book()

        payload = {
            'book': book.id
        }

        res = self.client.post(LIKEDITEM_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

        likeditem = LikedItem.objects.get(id=res.data['id'])

        self.assertEqual(likeditem.book.id, payload['book'])
        self.assertEqual(likeditem.user, user)

    def test_likeditems_delete(self):
        """Test deleting a likeditem."""
        user = sample_user()
        book = sample_book()

        self.client.force_authenticate(user)

        likeditem = LikedItem.objects.create(
            user=user,
            book=book,
        )
        url = detail_url(likeditem.id)
        res = self.client.delete(url)

        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        likeditems = LikedItem.objects.all()
        self.assertFalse(likeditems.exists())
