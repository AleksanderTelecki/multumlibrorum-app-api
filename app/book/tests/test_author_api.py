"""
Test for author API.
"""

from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import TestCase

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Author

from book.serializers import AuthorSerializer

AUTHOR_URL = reverse('book:author-list')


def detail_url(author_id):
    return reverse('book:author-detail', args=[author_id])


class PublicAuthorsApiTests(TestCase):
    """Test unauthenticated API requests."""

    def setUp(self):
        self.client = APIClient()

    def test_auth_not_required(self):
        """Test auth is not required for retrieving authors"""
        Author.objects.create(name='Luther king')
        Author.objects.create(name='Jake London')

        res = self.client.get(AUTHOR_URL)

        authors = Author.objects.all().order_by('-name')
        serializer = AuthorSerializer(authors, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)


class PrivateAuthorsApiTests(TestCase):
    """Test admin API requests."""

    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_superuser(
            'test@example.com',
            'testpass123',
        )
        self.client.force_authenticate(self.user)

    def test_update_author(self):
        """Test update an author."""
        author = Author.objects.create(name='Test Author')

        payload = {'name': 'Test Updated Author'}
        url = detail_url(author.id)

        res = self.client.patch(url, payload)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        author.refresh_from_db()
        self.assertEqual(author.name, payload['name'])

    def test_delete_author(self):
        """Test delete an author."""
        author = Author.objects.create(name='Test Auhtor')

        url = detail_url(author.id)
        res = self.client.delete(url)

        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        authors = Author.objects.all()
        self.assertFalse(authors.exists())
