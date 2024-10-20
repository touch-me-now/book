from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from django.db.models.query import RawQuerySet
from django.utils.translation import gettext_lazy as _


class Category(models.Model):
    slug = models.SlugField(max_length=255, primary_key=True)
    title = models.CharField(max_length=255)

    class Meta:
        ordering = ["slug"]
        verbose_name_plural = _('Categories')


class Book(models.Model):
    title = models.CharField(max_length=255)
    author = models.CharField(max_length=255)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name="books")
    description = models.TextField(blank=True, null=True)
    cover_img = models.ImageField(upload_to="books", blank=True, null=True)
    rating = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])

    class Meta:
        ordering = ["id"]


class ReviewQuerySet(models.QuerySet):
    def reviews_with_reactions(self) -> RawQuerySet:
        return self.raw(
            f"""
            SELECT 
                br.id,
                br.book_id,
                br.user_id,
                br.comment,
                br.rating,
                br.created_at,
                ARRAY_AGG(
                    CASE 
                        WHEN rr.reaction IS NOT null THEN 
                        JSON_BUILD_OBJECT(
                            'reaction', rr.reaction,
                            'count', rr.count
                        )
                    END
                ) AS reactions
            FROM book_review br
            LEFT JOIN (
                SELECT
                    review_id,
                    reaction,
                    COUNT(reaction) AS count
                FROM book_reviewreaction
                GROUP BY review_id, reaction
            ) rr ON br.id = rr.review_id
            GROUP BY br.id
            """
        )


def get_sentinel_user():
    sentinel_user, _ = get_user_model().objects.get_or_create(username="deleted", is_active=False)
    return sentinel_user


class Review(models.Model):
    objects = ReviewQuerySet.as_manager()

    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name="reviews")
    user = models.ForeignKey(get_user_model(), on_delete=models.SET(get_sentinel_user), related_name="reviews")
    comment = models.TextField(blank=True, null=True)
    rating = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    created_at = models.DateTimeField(auto_now_add=True)

    @property
    def author(self):
        return self.user.username

    class Meta:
        ordering = ["id"]


class ReviewReaction(models.Model):
    class Reaction(models.TextChoices):
        # I thought it would be nice to leave the possibility in the future
        # to be able to expand the types of user reactions
        like = "LIKE", _("like")
        dislike = "DIS", _("dislike")

    user = models.ForeignKey(get_user_model(), on_delete=models.SET(get_sentinel_user), related_name="review_reacts")
    review = models.ForeignKey(Review, on_delete=models.CASCADE, related_name="reacts")
    reaction = models.CharField(max_length=4, choices=Reaction.choices, default=Reaction.like)

    class Meta:
        constraints = (
            models.UniqueConstraint(
                fields=["review_id", "user_id"],
                name="unique_user_react"
            ),
        )
