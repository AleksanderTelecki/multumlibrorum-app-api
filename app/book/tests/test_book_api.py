"""
Tests for book APIs.
"""

from datetime import date
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Book, Genre, Author, Language, BookShelf
from book.serializers import BookSerializer, BookDetailSerializer


BOOK_URL = reverse('book:book-list')


def detail_url(book_id):
    """Create and return a book URL."""
    return reverse('book:book-detail', args=[book_id])


def create_book(**params):
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


class PublicBookAPITests(TestCase):
    """Test unauthenticated API requests."""

    def setUp(self):
        self.client = APIClient()

    def test_auth_not_required(self):
        """Test auth is not required to call API."""
        res = self.client.get(BOOK_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_retrive_books(self):
        """Test retrieving a list of books."""
        create_book()
        create_book()

        res = self.client.get(BOOK_URL)

        books = Book.objects.all().order_by('-id')
        serializer = BookSerializer(books, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_get_book_detail(self):
        """Test get book detail."""
        book = create_book()

        url = detail_url(book.id)
        res = self.client.get(url)

        serializer = BookDetailSerializer(book)

        self.assertEqual(res.data, serializer.data)

    def test_create_book_non_admin(self):
        """Test creating a book."""
        user = get_user_model().objects.create_user(
            'test@example.com',
            'testpass123',
        )
        self.client.force_authenticate(user)

        payload = {
            'title': 'Sample book title',
            'isbn13': '978-3-16-148410-0',
            'publication_date': date(2022, 5, 7),
            'available_quantity': 25,
            'price': Decimal('5.50'),
            'description': 'Sample Book description'
        }

        res = self.client.post(BOOK_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)


class PrivateBookAPITests(TestCase):
    """Test admin API requests."""

    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_superuser(
            'test@example.com',
            'testpass123',
        )
        self.client.force_authenticate(self.user)

    def test_create_book(self):
        """Test creating a book."""
        payload = {
            'title': 'Sample book title',
            'isbn13': '978-3-16-148410-0',
            'publication_date': date(2022, 5, 7),
            'available_quantity': 25,
            'price': Decimal('5.50'),
            'description': 'Sample Book description'
        }

        res = self.client.post(BOOK_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

        book = Book.objects.get(id=res.data['id'])

        for k, v in payload.items():
            self.assertEqual(getattr(book, k), v)

    def test_partial_update(self):
        """Test partial update of a book."""
        original_isbn13 = '978-3-16-148410-2'

        book = create_book(isbn13=original_isbn13)

        payload = {'title': 'New title'}

        url = detail_url(book.id)
        res = self.client.patch(url, payload)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        book.refresh_from_db()
        self.assertEqual(book.title, payload['title'])
        self.assertEqual(book.isbn13, original_isbn13)

    def test_full_update(self):
        """Test full update of a book."""
        book = create_book()

        payload = {
            'title': 'updated book title',
            'isbn13': '978-3-15-148410-0',
            'publication_date': date(2022, 6, 7),
            'available_quantity': 40,
            'price': Decimal('5.70'),
            'description': 'SUpdated description'
        }

        url = detail_url(book.id)
        res = self.client.put(url, payload)

        self.assertEqual(res.status_code, status.HTTP_200_OK)

        book.refresh_from_db()

        for k, v in payload.items():
            self.assertEqual(getattr(book, k), v)

    def test_delete_book(self):
        """Test deleting a book successful."""
        book = create_book()

        url = detail_url(book.id)
        res = self.client.delete(url)

        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Book.objects.filter(id=book.id).exists())

    def test_create_book_with_genre(self):
        """Test creating a book with genres."""
        payload = {
            'title': 'Test title',
            'isbn13': '978-3-15-148410-0',
            'publication_date': date(2022, 6, 7),
            'available_quantity': 40,
            'price': Decimal('5.70'),
            'description': 'Test description',
            'genres': [
                {'name': 'Sience Fiction', 'description': 'Very interesting'},
                {'name': 'Fiction', 'description': 'Questions i have'}
            ]
        }
        res = self.client.post(BOOK_URL, payload, format='json')

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        books = Book.objects.all()
        self.assertEqual(books.count(), 1)
        book = books[0]
        self.assertEqual(book.genres.count(), 2)

        for genre in payload['genres']:
            exists = book.genres.filter(name=genre['name']).exists()
            self.assertTrue(exists)

    def test_create_book_with_existing_genre(self):
        """Test creating genre when updating a book with existing genre."""
        genre_fiction = Genre.objects.create(
            name='Fiction',
            description='Fiction litreture.'
        )
        payload = {
            'title': 'Test title',
            'isbn13': '978-3-15-148410-0',
            'publication_date': date(2022, 6, 7),
            'available_quantity': 40,
            'price': Decimal('5.70'),
            'description': 'Test description',
            'genres': [
                {'name': 'Sience Fiction', 'description': 'Very interesting'},
                {'name': 'Fiction', 'description': 'Fiction litreture.'}
            ]
        }

        res = self.client.post(BOOK_URL, payload, format='json')

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

        books = Book.objects.all()

        self.assertEqual(books.count(), 1)

        book = books[0]

        self.assertEqual(book.genres.count(), 2)
        self.assertIn(genre_fiction, book.genres.all())

        for genre in payload['genres']:
            exists = book.genres.filter(name=genre['name']).exists()
            self.assertTrue(exists)

    def test_create_genre_on_update(self):
        """Test creating genre when updating a book."""
        book = create_book()

        payload = {'genres': [{'name': 'Fiction', 'description': 'New Desc'}]}
        url = detail_url(book.id)
        res = self.client.patch(url, payload, format='json')

        self.assertEqual(res.status_code, status.HTTP_200_OK)

        new_genre = Genre.objects.get(name='Fiction', description='New Desc')
        self.assertIn(new_genre, book.genres.all())

    def test_update_book_assign_genre(self):
        """Test assigning an existing genre when updating a book."""
        genre_fiction = Genre.objects.create(
            name='Fiction',
            description='Fiction litreture.'
        )
        book = create_book()
        book.genres.add(genre_fiction)

        genre_sfiction = Genre.objects.create(
            name='Science Fiction',
            description='Science Fiction litreture.'
        )
        payload = {
            'genres': [
                {
                    'name': 'Science Fiction',
                    'description': 'Science Fiction litreture.'
                }
            ]
        }

        url = detail_url(book.id)
        res = self.client.patch(url, payload, format='json')

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn(genre_sfiction, book.genres.all())
        self.assertNotIn(genre_fiction, book.genres.all())

    def test_clear_genres(self):
        """Test clear book genres."""
        genre = Genre.objects.create(
            name='Fiction',
            description='Fiction litreture.'
        )
        book = create_book()
        book.genres.add(genre)

        payload = {'genres': []}
        url = detail_url(book.id)

        res = self.client.patch(url, payload, format='json')

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(book.genres.count(), 0)

    def test_create_book_with_new_author(self):
        """Test creating a book with new authors"""
        payload = {
            'title': 'Test title',
            'isbn13': '978-3-15-148410-0',
            'publication_date': date(2022, 6, 7),
            'available_quantity': 40,
            'price': Decimal('5.70'),
            'description': 'Test description',
            'authors': [
                {'name': 'Test author 1'},
                {'name': 'Test author 2'}
            ]
        }

        res = self.client.post(BOOK_URL, payload, format='json')

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        books = Book.objects.all()
        self.assertEqual(books.count(), 1)
        book = books[0]
        self.assertEqual(book.authors.count(), 2)
        for author in payload['authors']:
            exists = book.authors.filter(name=author['name']).exists()
            self.assertTrue(exists)

    def test_create_book_with_existing_author(self):
        author = Author.objects.create(name='Test author 1')
        payload = {
            'title': 'Test title',
            'isbn13': '978-3-15-148410-0',
            'publication_date': date(2022, 6, 7),
            'available_quantity': 40,
            'price': Decimal('5.70'),
            'description': 'Test description',
            'authors': [
                {'name': 'Test author 1'},
                {'name': 'Test author 2'}
            ]
        }

        res = self.client.post(BOOK_URL, payload, format='json')
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        books = Book.objects.all()
        self.assertEqual(books.count(), 1)
        book = books[0]
        self.assertEqual(book.authors.count(), 2)
        self.assertIn(author, book.authors.all())

        for author in payload['authors']:
            exists = book.authors.filter(name=author['name']).exists()
            self.assertTrue(exists)

    def test_create_author_on_update(self):
        """Test creating an author when updating a book."""
        book = create_book()

        payload = {'authors': [{'name': 'Test author 1'}]}
        url = detail_url(book.id)
        res = self.client.patch(url, payload, format='json')

        self.assertEqual(res.status_code, status.HTTP_200_OK)

        new_author = Author.objects.get(name='Test author 1')
        self.assertIn(new_author, book.authors.all())

    def test_update_book_assign_author(self):
        """Test assigning an existing author when updating a book."""
        author1 = Author.objects.create(name='Test author 1')
        book = create_book()
        book.authors.add(author1)

        author2 = Author.objects.create(name='Test author 2')

        payload = {'authors': [{'name': 'Test author 2'}]}
        url = detail_url(book.id)
        res = self.client.patch(url, payload, format='json')

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn(author2, book.authors.all())
        self.assertNotIn(author1, book.authors.all())

    def test_clear_book_authors(self):
        """Test clear an book authors."""
        author = Author.objects.create(name='Test author')
        book = create_book()
        book.authors.add(author)

        payload = {'authors': []}
        url = detail_url(book.id)
        res = self.client.patch(url, payload, format='json')

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(book.authors.count(), 0)

    def test_create_book_with_new_language(self):
        """Test creating a book with new languages"""
        payload = {
            'title': 'Test title',
            'isbn13': '978-3-15-148410-0',
            'publication_date': date(2022, 6, 7),
            'available_quantity': 40,
            'price': Decimal('5.70'),
            'description': 'Test description',
            'languages': [
                {'name': 'Test language 1'},
                {'name': 'Test language 2'}
            ]
        }

        res = self.client.post(BOOK_URL, payload, format='json')

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        books = Book.objects.all()
        self.assertEqual(books.count(), 1)
        book = books[0]
        self.assertEqual(book.languages.count(), 2)
        for language in payload['languages']:
            exists = book.languages.filter(name=language['name']).exists()
            self.assertTrue(exists)

    def test_create_book_with_existing_language(self):
        language = Language.objects.create(name='Test language 1')
        payload = {
            'title': 'Test title',
            'isbn13': '978-3-15-148410-0',
            'publication_date': date(2022, 6, 7),
            'available_quantity': 40,
            'price': Decimal('5.70'),
            'description': 'Test description',
            'languages': [
                {'name': 'Test language 1'},
                {'name': 'Test language 2'}
            ]
        }

        res = self.client.post(BOOK_URL, payload, format='json')
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        books = Book.objects.all()
        self.assertEqual(books.count(), 1)
        book = books[0]
        self.assertEqual(book.languages.count(), 2)
        self.assertIn(language, book.languages.all())

        for language in payload['languages']:
            exists = book.languages.filter(name=language['name']).exists()
            self.assertTrue(exists)

    def test_create_language_on_update(self):
        """Test creating an language when updating a book."""
        book = create_book()

        payload = {'languages': [{'name': 'Test language 1'}]}
        url = detail_url(book.id)
        res = self.client.patch(url, payload, format='json')

        self.assertEqual(res.status_code, status.HTTP_200_OK)

        new_language = Language.objects.get(name='Test language 1')
        self.assertIn(new_language, book.languages.all())

    def test_update_book_assign_language(self):
        """Test assigning an existing language when updating a book."""
        language1 = Language.objects.create(name='Test language 1')
        book = create_book()
        book.languages.add(language1)

        language2 = Language.objects.create(name='Test language 2')

        payload = {'languages': [{'name': 'Test language 2'}]}
        url = detail_url(book.id)
        res = self.client.patch(url, payload, format='json')

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn(language2, book.languages.all())
        self.assertNotIn(language1, book.languages.all())

    def test_clear_book_languages(self):
        """Test clear an book languages."""
        language = Language.objects.create(name='Test language')
        book = create_book()
        book.languages.add(language)

        payload = {'languages': []}
        url = detail_url(book.id)
        res = self.client.patch(url, payload, format='json')

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(book.languages.count(), 0)

    def test_create_book_with_new_bookshelf(self):
        """Test creating a book with new bookshelves"""
        payload = {
            'title': 'Test title',
            'isbn13': '978-3-15-148410-0',
            'publication_date': date(2022, 6, 7),
            'available_quantity': 40,
            'price': Decimal('5.70'),
            'description': 'Test description',
            'bookshelves': [
                {
                    'name': 'Test bookshelf 1',
                    'deescription': 'bloody dracula.'
                },
                {
                    'name': 'Test bookshelf 2'
                }
            ]
        }

        res = self.client.post(BOOK_URL, payload, format='json')

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        books = Book.objects.all()
        self.assertEqual(books.count(), 1)
        book = books[0]
        self.assertEqual(book.bookshelves.count(), 2)
        for bookshelf in payload['bookshelves']:
            exists = book.bookshelves.filter(name=bookshelf['name']).exists()
            self.assertTrue(exists)

    def test_create_book_with_existing_bookshelf(self):
        bookshelf = BookShelf.objects.create(
            name='Test bookshelf 1',
            description='bloody dracula.'
        )
        payload = {
            'title': 'Test title',
            'isbn13': '978-3-15-148410-0',
            'publication_date': date(2022, 6, 7),
            'available_quantity': 40,
            'price': Decimal('5.70'),
            'description': 'Test description',
            'bookshelves': [
                {'name': 'Test bookshelf 1', 'description': 'bloody dracula.'},
                {'name': 'Test bookshelf 2'}
            ]
        }

        res = self.client.post(BOOK_URL, payload, format='json')
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        books = Book.objects.all()
        self.assertEqual(books.count(), 1)
        book = books[0]
        self.assertEqual(book.bookshelves.count(), 2)
        self.assertIn(bookshelf, book.bookshelves.all())

        for bookshelf in payload['bookshelves']:
            exists = book.bookshelves.filter(name=bookshelf['name']).exists()
            self.assertTrue(exists)

    def test_create_bookshelf_on_update(self):
        """Test creating an bookshelf when updating a book."""
        book = create_book()

        payload = {'bookshelves': [
                {
                    'name': 'Test bookshelf 1',
                    'description': 'bloody dracula'
                }
            ]
        }
        url = detail_url(book.id)
        res = self.client.patch(url, payload, format='json')

        self.assertEqual(res.status_code, status.HTTP_200_OK)

        new_bookshelf = BookShelf.objects.get(name='Test bookshelf 1')
        self.assertIn(new_bookshelf, book.bookshelves.all())

    def test_update_book_assign_bookshelf(self):
        """Test assigning an existing bookshelf when updating a book."""
        bookshelf1 = BookShelf.objects.create(name='Test bookshelf 1')
        book = create_book()
        book.bookshelves.add(bookshelf1)

        bookshelf2 = BookShelf.objects.create(name='Test bookshelf 2')

        payload = {'bookshelves': [{'name': 'Test bookshelf 2'}]}
        url = detail_url(book.id)
        res = self.client.patch(url, payload, format='json')

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn(bookshelf2, book.bookshelves.all())
        self.assertNotIn(bookshelf1, book.bookshelves.all())

    def test_clear_book_bookshelf(self):
        """Test clear an book bookshelves."""
        bookshelf = BookShelf.objects.create(name='Test bookshelf')
        book = create_book()
        book.bookshelves.add(bookshelf)

        payload = {'bookshelves': []}
        url = detail_url(book.id)
        res = self.client.patch(url, payload, format='json')

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(book.bookshelves.count(), 0)
