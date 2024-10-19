from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from django.utils.translation import gettext_lazy as _


class Category(models.Model):
    title = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255)

    class Meta:
        verbose_name_plural = _('Categories')


class Book(models.Model):
    title = models.CharField(max_length=255)
    author = models.CharField(max_length=255)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name="books")
    description = models.TextField(blank=True, null=True)
    cover_img = models.ImageField(upload_to="books", blank=True, null=True)
    rating = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])


class Review(models.Model):
    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name="reviews")
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE, related_name="reviews")
    comment = models.TextField(blank=True, null=True)
    rating = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    created_at = models.DateTimeField(auto_now_add=True)


def get_sentinel_user():
    sentinel_user, _ = get_user_model().objects.get_or_create(username="deleted")
    return sentinel_user


class ReviewLike(models.Model):
    review = models.ForeignKey(Review, on_delete=models.CASCADE, related_name="likes")
    user = models.ForeignKey(get_user_model(), on_delete=models.SET(get_sentinel_user), related_name="likes")
    is_dislike = models.BooleanField(default=False)

    class Meta:
        unique_together = ["review", "user"]
