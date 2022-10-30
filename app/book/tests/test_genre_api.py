"""
Tests for the API.
"""
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import TestCase

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Genre

from book.serializers import GenreSerializer

GENRE_URL = reverse('book:genre-list')


def detail_url(genre_id):
    return reverse('book:genre-detail', args=[genre_id])


class PublicGenresApiTests(TestCase):
    """Test api genres request."""

    def setUp(self):
        self.client = APIClient()

    def test_retrieve_genres(self):
        """Test list of genres."""

        Genre.objects.create(name='Test 1', description='Test also 1')
        Genre.objects.create(name='Test 2', description='Test also 2')

        res = self.client.get(GENRE_URL)

        genres = Genre.objects.all().order_by('-name')
        serializer = GenreSerializer(genres, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)


class PrivateGenresApiTests(TestCase):
    """Test genres requests for admin user"""

    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_superuser(
            'test@example.com',
            'testpass123',
        )
        self.client.force_authenticate(self.user)

    def test_genres_patch(self):
        """Test genre update."""
        genre = Genre.objects.create(name='Test 1', description='Test also 1')

        payload = {'name': 'Test upd 1', 'description': 'Test also upd 1'}

        url = detail_url(genre.id)
        res = self.client.patch(url, payload)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        genre.refresh_from_db()
        self.assertEqual(genre.name, payload['name'])

    def test_genres_put(self):
        """Test genre update."""
        genre = Genre.objects.create(name='Test 1', description='Test also 1')

        payload = {'name': 'Test upd 1', 'description': 'Test also upd 1'}

        url = detail_url(genre.id)
        res = self.client.put(url, payload)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        genre.refresh_from_db()
        self.assertEqual(genre.name, payload['name'])

    def test_genres_delete(self):
        """Test deleting a genre"""
        genre = Genre.objects.create(name='Test 1', description='Test also 1')

        url = detail_url(genre.id)
        res = self.client.delete(url)

        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        genres = Genre.objects.all()
        self.assertFalse(genres.exists())
