from django.contrib import admin

from book.models import Category, Book, Review, ReviewReaction

admin.site.register(Category)
admin.site.register(Book)
admin.site.register(Review)
admin.site.register(ReviewReaction)
