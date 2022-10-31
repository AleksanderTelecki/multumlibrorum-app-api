"""
Tests for the publishers API.
"""
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import TestCase

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Publisher

from book.serializers import PublisherSerializer

PUBLISHER_URL = reverse('book:publisher-list')


def detail_url(publisher_id):
    return reverse('book:publisher-detail', args=[publisher_id])


class PublicPublishersApiTests(TestCase):
    """Test api publishers request."""

    def setUp(self):
        self.client = APIClient()

    def test_retrieve_publishers(self):
        """Test list of publishers."""

        Publisher.objects.create(name='Test 1', description='Test also 1')
        Publisher.objects.create(name='Test 2', description='Test also 2')

        res = self.client.get(PUBLISHER_URL)

        publishers = Publisher.objects.all().order_by('-name')
        serializer = PublisherSerializer(publishers, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)


class PrivatePublishersApiTests(TestCase):
    """Test publishers requests for admin user"""

    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_superuser(
            'test@example.com',
            'testpass123',
        )
        self.client.force_authenticate(self.user)

    def test_publishers_patch(self):
        """Test publisher update."""
        publisher = Publisher.objects.create(
            name='Test 1',
            description='Test also 1'
        )

        payload = {'name': 'Test upd 1', 'description': 'Test also upd 1'}

        url = detail_url(publisher.id)
        res = self.client.patch(url, payload)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        publisher.refresh_from_db()
        self.assertEqual(publisher.name, payload['name'])

    def test_publishers_put(self):
        """Test publisher update."""
        publisher = Publisher.objects.create(
            name='Test 1',
            description='Test also 1'
        )

        payload = {'name': 'Test upd 1', 'description': 'Test also upd 1'}

        url = detail_url(publisher.id)
        res = self.client.put(url, payload)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        publisher.refresh_from_db()
        self.assertEqual(publisher.name, payload['name'])

    def test_publishers_delete(self):
        """Test deleting a publisher"""
        publisher = Publisher.objects.create(
            name='Test 1',
            description='Test also 1'
        )

        url = detail_url(publisher.id)
        res = self.client.delete(url)

        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        publishers = Publisher.objects.all()
        self.assertFalse(publishers.exists())
