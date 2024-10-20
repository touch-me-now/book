from django.urls import path, include, re_path
from rest_framework.routers import SimpleRouter

from book.views import (
    BookViewSet, ReviewListAPIView, ReviewCreateAPIView, ReviewDestroyAPIView,
    ReviewReactionAPIView
)

router = SimpleRouter()
router.register('', BookViewSet, basename="books")

urlpatterns = [
    re_path('^reviews/$', ReviewCreateAPIView.as_view(), name='book-reviews-create'),
    re_path('^reviews/(?P<pk>.+)$', ReviewDestroyAPIView.as_view(), name='book-reviews-destroy'),
    path('', include(router.urls)),
    re_path('^(?P<book_id>.+)/reviews/$', ReviewListAPIView.as_view(), name='book-reviews-list'),

    re_path('^react/reviews/(?P<review_id>.+)/$', ReviewReactionAPIView.as_view(),
            name='book-review-react'),
]
