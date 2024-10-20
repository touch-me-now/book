from django.db.models import Avg
from django.db.models.signals import post_save
from django.dispatch import receiver

from book.models import Review


@receiver(post_save, sender=Review)
def update_book_rating(sender, instance, created, **kwargs):
    book = instance.book
    avg_rating = book.reviews.aggregate(avg_rating=Avg("rating", default=0))["avg_rating"]

    if avg_rating >= 5:
        book.rating = 5
    elif avg_rating <= 1:
        book.rating = 1
    else:
        book.rating = avg_rating

    book.save()
