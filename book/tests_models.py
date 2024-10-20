from unittest import mock

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from django.db.models.query import RawQuerySet
from django.db.models.signals import post_save
from django.test import TestCase

from book.models import Review, Category, Book, ReviewReaction

user_model = get_user_model()


class BookTest(TestCase):
    def setUp(self):
        self.test_category = Category.objects.create(title="test_cat", slug="test_cat")
        self.test_book = Book(
            title="test_book",
            author="someone",
            category=self.test_category,
            rating=1
        )

    def test_rating_validation(self):
        # low then 1
        with self.assertRaises(ValidationError):
            self.test_book.rating = 0
            self.test_book.full_clean()

        # grater then 5
        with self.assertRaises(ValidationError):
            self.test_book.rating = 6
            self.test_book.full_clean()


class ReviewTest(TestCase):
    def setUp(self):
        self.test_category = Category.objects.create(title="test_cat", slug="test_cat")
        self.test_book = Book.objects.create(
            title="test_book",
            author="someone",
            category=self.test_category,
            rating=1
        )
        self.test_user = user_model.objects.create_user(username="test")

    def test_update_book_rating_via_signal(self):
        usr_rating = 3

        with mock.patch("book.signals.update_book_rating", autospec=True) as mock_update_book_rating:
            post_save.connect(mock_update_book_rating, sender=Review)
            review = Review.objects.create(
                book=self.test_book,
                user=self.test_user,
                rating=usr_rating
            )
            mock_update_book_rating.assert_called_with(
                signal=post_save,
                sender=Review,
                instance=review,
                created=True,
                update_fields=None,
                raw=False,
                using='default'
            )

        self.assertTrue(mock_update_book_rating.called)
        self.assertEquals(mock_update_book_rating.call_count, 1)

        self.test_book.refresh_from_db()
        self.assertEquals(self.test_book.rating, usr_rating)

    def test_sentinel_user_on_remove_user(self):
        remove_usr = user_model.objects.create_user(username="remove_usr")
        review = Review.objects.create(
            book=self.test_book,
            user=remove_usr,
            rating=1
        )
        remove_usr.delete()
        review.refresh_from_db()

        self.assertIsNotNone(review.user)
        self.assertNotEqual(review.user.username, "remove_usr")
        self.assertEquals(review.user.username, "deleted")
        self.assertFalse(review.user.is_active)

    def test_rating_validation(self):
        # low then 1
        with self.assertRaises(ValidationError):
            self.test_book.rating = 0
            self.test_book.full_clean()

        # grater then 5
        with self.assertRaises(ValidationError):
            self.test_book.rating = 6
            self.test_book.full_clean()


class ReviewReactionTest(TestCase):
    def setUp(self):
        self.test_category = Category.objects.create(title="test_cat", slug="test_cat")
        self.test_book = Book.objects.create(
            title="test_book",
            author="someone",
            category=self.test_category,
            rating=1
        )
        self.test_user = user_model.objects.create_user(username="test")
        self.test_review = Review.objects.create(
            book=self.test_book,
            user=self.test_user,
            rating=3
        )

    def test_constraint_unique_user_and_review(self):
        ReviewReaction.objects.create(
            user=self.test_user,
            review=self.test_review,
            reaction=ReviewReaction.Reaction.like
        )

        with self.assertRaises(IntegrityError):
            ReviewReaction.objects.create(
                user=self.test_user,
                review=self.test_review,
                reaction=ReviewReaction.Reaction.dislike
            )

    def test_sentinel_user_on_remove_user(self):
        remove_usr = user_model.objects.create_user(username="remove_usr")
        reaction = ReviewReaction.objects.create(
            user=remove_usr,
            review=self.test_review,
            reaction=ReviewReaction.Reaction.like
        )
        remove_usr.delete()
        reaction.refresh_from_db()

        self.assertIsNotNone(reaction.user)
        self.assertNotEqual(reaction.user.username, "remove_usr")
        self.assertEquals(reaction.user.username, "deleted")
        self.assertFalse(reaction.user.is_active)

    def test_review_with_reactions(self):
        reviews = Review.objects.reviews_with_reactions()

        self.assertIsInstance(reviews, RawQuerySet)
        self.assertGreater(len(reviews), 0)

        first_review = reviews[0]
        self.assertTrue(hasattr(first_review, "reactions"))
