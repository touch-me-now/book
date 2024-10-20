from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy
from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.test import APITestCase
from rest_framework_simplejwt.tokens import RefreshToken

from book.models import Category, Book, Review, ReviewReaction
from book.views import ReviewCreateAPIView

user_model = get_user_model()


class BookAPITest(APITestCase):
    def setUp(self):
        self.test_category = Category.objects.create(slug="test_cat", title="test_cat")
        self.test_book = Book.objects.create(title="test_book", author="someone", category=self.test_category, rating=1)

        self.list_url = reverse('books-list')

    def test_success_list(self):
        response = self.client.get(self.list_url)
        self.assertEquals(response.status_code, status.HTTP_200_OK)

        data = response.json()
        self.assertIn("results", data)
        self.assertEquals(len(data["results"]), 1)

    def test_filtering_by_category(self):
        response = self.client.get(self.list_url, data={"category": self.test_category.slug})
        self.assertEquals(response.status_code, status.HTTP_200_OK)

        data = response.json()
        self.assertIn("results", data)
        self.assertGreaterEqual(len(data["results"]), 1)
        first_book = data["results"][0]
        self.assertIn("category", first_book)
        self.assertIsInstance(first_book["category"], dict)
        self.assertIn("title", first_book["category"])
        self.assertIn(first_book["category"]["title"], self.test_category.title)

    def test_search_by_title(self):
        response = self.client.get(self.list_url, data={"search": "tes"})
        self.assertEquals(response.status_code, status.HTTP_200_OK)

        data = response.json()
        self.assertIn("results", data)
        self.assertGreaterEqual(len(data["results"]), 1)
        first_book = data["results"][0]
        self.assertIn("title", first_book)
        self.assertIn("tes", first_book["title"])

    def test_pagination(self):
        response = self.client.get(self.list_url, data={"page": 2})
        self.assertEquals(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_success_detail(self):
        url = reverse('books-detail', args=[self.test_book.id])
        response = self.client.get(url)
        self.assertEquals(response.status_code, status.HTTP_200_OK)


class ReviewAPITest(APITestCase):
    def setUp(self):
        self.test_user = user_model.objects.create_user(username="test", password="secret")
        self._token = RefreshToken.for_user(user=self.test_user)
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + str(self._token.access_token))

        self.test_category = Category.objects.create(title="test_cat", slug="test_cat")
        self.test_book = Book.objects.create(title="test_book", author="someone", category=self.test_category, rating=1)
        self.test_review = Review.objects.create(book=self.test_book, user=self.test_user, rating=1)

    def test_success_list(self):
        url = reverse("book-reviews-list", args=[self.test_review.id])
        response = self.client.get(url)
        self.assertEquals(response.status_code, status.HTTP_200_OK)
        data = response.json()
        self.assertIn("results", data)
        self.assertEquals(len(data["results"]), 1)

    def test_create_review(self):
        ReviewCreateAPIView.throttle_classes = ()  # to avoid throttling
        url = reverse("book-reviews-create")
        data = {"book": self.test_book.id, "rating": 1}
        response = self.client.post(url, data)
        self.assertEquals(response.status_code, status.HTTP_201_CREATED, response.json())

    def test_remove_review(self):
        review_author = user_model.objects.create_user(username="test2")
        token = RefreshToken.for_user(user=review_author)
        test_review = Review.objects.create(book=self.test_book, user=review_author, rating=1)

        url = reverse("book-reviews-destroy", args=[test_review.id])
        # req from self.test_user to delete
        response_for_not_author = self.client.delete(url)
        self.assertEquals(response_for_not_author.status_code, status.HTTP_403_FORBIDDEN)

        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + str(token.access_token))

        response_for_author = self.client.delete(url, headers={"Authorization": "Bearer " + str(token.access_token)})
        self.assertEqual(response_for_author.status_code, status.HTTP_204_NO_CONTENT)

        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + str(self._token.access_token))


class ReviewReactionAPITest(APITestCase):
    def setUp(self):
        self.react_user = user_model.objects.create_user(username="react_usr", password="secret")
        token = RefreshToken.for_user(user=self.react_user)
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + str(token.access_token))

        self.test_user = user_model.objects.create_user(username="test", password="secret")
        self.test_category = Category.objects.create(title="test_cat", slug="test_cat")
        self.test_book = Book.objects.create(title="test_book", author="someone", category=self.test_category, rating=1)

    def test_create_react(self):
        test_review = Review.objects.create(book=self.test_book, user=self.test_user, rating=1)

        url = reverse("book-review-react", args=[test_review.id])
        data = {"reaction": ReviewReaction.Reaction.like.value}

        response = self.client.post(url, data)
        self.assertEquals(response.status_code, status.HTTP_201_CREATED, response.json())

    def test_failure_create_on_exist(self):
        test_review = Review.objects.create(book=self.test_book, user=self.test_user, rating=1)
        ReviewReaction.objects.create(
            review=test_review,
            user=self.react_user,
            reaction=ReviewReaction.Reaction.dislike
        )

        url = reverse("book-review-react", args=[test_review.id])
        data = {"reaction": ReviewReaction.Reaction.like.value}

        response = self.client.post(url, data)
        self.assertEquals(response.status_code, status.HTTP_400_BAD_REQUEST, response.json())

        resp_data = response.json()
        self.assertIn("detail", resp_data)
        self.assertIn(gettext_lazy("Already exists! Try update"), resp_data["detail"])

    def test_update_react(self):
        test_review = Review.objects.create(book=self.test_book, user=self.test_user, rating=5)
        react = ReviewReaction.objects.create(
            review=test_review,
            user=self.react_user,
            reaction=ReviewReaction.Reaction.dislike
        )
        self.assertEquals(react.reaction, ReviewReaction.Reaction.dislike)

        url = reverse("book-review-react", args=[test_review.id])
        data = {"reaction": ReviewReaction.Reaction.like.value}

        response = self.client.patch(url, data)
        self.assertEquals(response.status_code, status.HTTP_200_OK, response.json())

        react.refresh_from_db()
        self.assertEquals(react.reaction, ReviewReaction.Reaction.like)
        self.assertEquals(react.review_id, test_review.id)
        self.assertEquals(react.user_id, self.react_user.id)

    def test_failure_update_not_exist(self):
        url = reverse("book-review-react", args=["not_exist"])
        data = {"reaction": ReviewReaction.Reaction.like.value}

        response = self.client.patch(url, data)
        self.assertEquals(response.status_code, status.HTTP_404_NOT_FOUND, response.json())
