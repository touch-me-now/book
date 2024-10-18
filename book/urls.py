from django.urls import path, include, re_path
from rest_framework.routers import SimpleRouter

from book.views import BookViewSet, ReviewListAPIView, ReviewCreateAPIView, like_review, dislike_review, unlike_review

router = SimpleRouter()
router.register('books', BookViewSet, basename="books")

urlpatterns = [
    path('books/reviews/', ReviewCreateAPIView.as_view(), name='book-reviews-create'),
    path('', include(router.urls)),
    re_path('^books/(?P<book_id>.+)/reviews/$', ReviewListAPIView.as_view(), name='book-reviews-list'),
    re_path('^reviews/(?P<review_id>.+)/like/$', like_review, name='book-reviews-like'),
    re_path('^reviews/(?P<review_id>.+)/dislike/$', dislike_review, name='book-reviews-dislike'),
    re_path('^reviews/(?P<review_id>.+)/unlike/$', unlike_review, name='book-reviews-unlike'),

]
