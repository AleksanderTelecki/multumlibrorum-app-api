"""
Tests for the lanuage API.
"""
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import TestCase

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Language

from book.serializers import LanguageSerializer

LANGUAGE_URL = reverse('book:language-list')


def detail_url(language_id):
    return reverse('book:language-detail', args=[language_id])


class PublicLanguagesApiTests(TestCase):
    """Test api languages request."""

    def setUp(self):
        self.client = APIClient()

    def test_retrieve_languages(self):
        """Test list of languages."""

        Language.objects.create(name='Test 1')
        Language.objects.create(name='Test 2')

        res = self.client.get(LANGUAGE_URL)

        languages = Language.objects.all().order_by('-name')
        serializer = LanguageSerializer(languages, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)


class PrivateLanguagesApiTests(TestCase):
    """Test languages requests for admin user"""

    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_superuser(
            'test@example.com',
            'testpass123',
        )
        self.client.force_authenticate(self.user)

    def test_languages_patch(self):
        """Test language update."""
        language = Language.objects.create(name='Test 1')

        payload = {'name': 'Test upd 1'}

        url = detail_url(language.id)
        res = self.client.patch(url, payload)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        language.refresh_from_db()
        self.assertEqual(language.name, payload['name'])

    def test_languages_put(self):
        """Test language update."""
        language = Language.objects.create(name='Test 1')

        payload = {'name': 'Test upd 1'}

        url = detail_url(language.id)
        res = self.client.put(url, payload)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        language.refresh_from_db()
        self.assertEqual(language.name, payload['name'])

    def test_languages_delete(self):
        """Test deleting a language"""
        language = Language.objects.create(name='Test 1')

        url = detail_url(language.id)
        res = self.client.delete(url)

        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        language = Language.objects.all()
        self.assertFalse(language.exists())
