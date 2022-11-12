"""
Tests for the orderitem API.
"""
from datetime import date
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import TestCase

from rest_framework import status
from rest_framework.test import APIClient

from core.models import OrderItem, Book

from order.serializers import OrderItemDetailSerializer

ORDERITEM_URL = reverse('order:orderitem-list')


def detail_url(orderitem_id):
    return reverse('order:orderitem-detail', args=[orderitem_id])


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


class PrivateOrderItemsApiTests(TestCase):
    """Test orderitems requests for authorized user."""

    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            'test@example.com',
            'testpass123',
        )
        self.client.force_authenticate(self.user)

    def test_retrieve_orderitems(self):
        """Test list of orderitems."""

        user = sample_user()
        book = sample_book()

        self.client.force_authenticate(user)

        OrderItem.objects.create(
            user=user,
            book=book,
            quantity=2
        )

        res = self.client.get(ORDERITEM_URL)

        orderitems = OrderItem.objects.all().filter(user=user) \
            .order_by('-book__title')
        serializer = OrderItemDetailSerializer(orderitems, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_create_orderitem(self):
        """Test adding an orderitem to cart."""
        user = sample_user()
        self.client.force_authenticate(user)
        book = sample_book()

        payload = {
            'book': book.id,
            'quantity': 2
        }

        res = self.client.post(ORDERITEM_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

        orderitem = OrderItem.objects.get(id=res.data['id'])

        self.assertEqual(orderitem.book.id, payload['book'])
        self.assertEqual(orderitem.user, user)
        self.assertEqual(orderitem.quantity, payload['quantity'])

    def test_orderitems_patch(self):
        """Test orderitems update."""

        user = sample_user()
        book = sample_book()

        self.client.force_authenticate(user)

        orderitem = OrderItem.objects.create(
            user=user,
            book=book,
            quantity=2
        )

        payload = {
            'book': book.id,
            'quantity': 10
        }

        url = detail_url(orderitem.id)
        res = self.client.patch(url, payload)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        orderitem.refresh_from_db()
        self.assertEqual(orderitem.quantity, payload['quantity'])

    def test_orderitems_delete(self):
        """Test deleting a orderitems."""
        user = sample_user()
        book = sample_book()

        self.client.force_authenticate(user)

        orderitem = OrderItem.objects.create(
            user=user,
            book=book,
            quantity=2
        )
        url = detail_url(orderitem.id)
        res = self.client.delete(url)

        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        orderitems = OrderItem.objects.all()
        self.assertFalse(orderitems.exists())

    def test_orderitem_add_book_quantity(self):
        """Test adding a orderitems with book quantity recalculation."""
        user = sample_user()
        self.client.force_authenticate(user)
        book = sample_book(available_quantity=10)
        old_quantity = book.available_quantity
        payload = {
            'book': book.id,
            'quantity': 2
        }

        res = self.client.post(ORDERITEM_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

        orderitem = OrderItem.objects.get(id=res.data['id'])

        self.assertEqual(orderitem.book.id, payload['book'])
        self.assertEqual(orderitem.user, user)
        self.assertEqual(orderitem.quantity, payload['quantity'])
        book.refresh_from_db()
        self.assertEqual(
            book.available_quantity,
            old_quantity-payload['quantity']
        )

    def test_orderitem_delete_book_quantity(self):
        """Test deleting a orderitems with book quantity recalculation."""
        user = sample_user()
        book = sample_book()
        old_quantity = book.available_quantity
        self.client.force_authenticate(user)

        orderitem = OrderItem.objects.create(
            user=user,
            book=book,
            quantity=2
        )
        url = detail_url(orderitem.id)
        res = self.client.delete(url)

        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        orderitems = OrderItem.objects.all()
        self.assertFalse(orderitems.exists())

        book.refresh_from_db()
        self.assertEqual(book.available_quantity, old_quantity)
