from django.db.models import Avg

from book.models import Book


def update_book_rating(book: Book):
    avg_rating = book.reviews.aggregate(avg_rating=Avg("rating", default=0))["avg_rating"]

    if avg_rating > 5:
        book.rating = 5
    elif avg_rating < 1:
        book.rating = 1
    else:
        book.rating = avg_rating

    book.save()
