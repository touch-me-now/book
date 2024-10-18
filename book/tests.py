from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.test import APITestCase
from rest_framework_simplejwt.tokens import RefreshToken

from book.models import Category, Book, Review

user_model = get_user_model()


class BookTest(APITestCase):
    def setUp(self):
        self.test_category = Category.objects.create(title="test", slug="test")
        self.test_book = Book.objects.create(title="test", author="test", category=self.test_category, rating=1)

    def test_success_list(self):
        url = reverse('books-list')
        response = self.client.get(url, format='json')
        self.assertEquals(response.status_code, status.HTTP_200_OK)
        data = response.json()
        self.assertIn("results", data)
        self.assertEquals(len(data["results"]), 1)

    def test_success_detail(self):
        url = reverse('books-detail', args=[self.test_book.id])
        response = self.client.get(url, format='json')
        self.assertEquals(response.status_code, status.HTTP_200_OK)


class ReviewTest(APITestCase):
    def setUp(self):
        self.test_user = user_model.objects.create_user(username="test", password="secret")
        self.refresh = RefreshToken.for_user(user=self.test_user)
        self.test_category = Category.objects.create(title="test", slug="test")
        self.test_book = Book.objects.create(title="test", author="test", category=self.test_category, rating=1)
        self.test_review = Review.objects.create(book=self.test_book, user=self.test_user, rating=1)

    def test_success_list(self):
        url = reverse("book-reviews-list", args=[self.test_review.id])
        response = self.client.get(url, format='json')
        self.assertEquals(response.status_code, status.HTTP_200_OK)
        data = response.json()
        self.assertIn("results", data)
        self.assertEquals(len(data["results"]), 1)

    def test_create_review(self):
        url = reverse("book-reviews-create")
        data = {"book": self.test_book.id, "rating": 1}
        response = self.client.post(url, data, format='json',
                                    headers={"Authorization": f"Bearer {self.refresh.access_token}"})
        self.assertEquals(response.status_code, status.HTTP_201_CREATED, response.json())
