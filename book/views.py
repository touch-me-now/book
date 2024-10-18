from http import HTTPMethod

from django.shortcuts import get_object_or_404
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from rest_framework import status
from rest_framework.decorators import permission_classes, api_view
from rest_framework.response import Response
from rest_framework.generics import ListAPIView, CreateAPIView
from rest_framework.filters import BaseFilterBackend, SearchFilter
from rest_framework.permissions import IsAuthenticated
from rest_framework.throttling import UserRateThrottle
from rest_framework.viewsets import ReadOnlyModelViewSet
from rest_framework.pagination import PageNumberPagination

from book.models import Book, Review, ReviewLike
from book.serializers import BookSerializer, ReviewSerializer


class BookCategoryFilter(BaseFilterBackend):
    category_param = "category_id"

    def filter_queryset(self, request, queryset, view):
        category_value = request.query_params.get(self.category_param, '')

        if category_value.isdigit():
            return queryset.filter(category_id=category_value)
        return queryset


class BookViewSet(ReadOnlyModelViewSet):
    queryset = Book.objects.select_related("category").all()
    serializer_class = BookSerializer
    pagination_class = PageNumberPagination
    filter_backends = (BookCategoryFilter, SearchFilter)
    search_fields = ["title"]

    @method_decorator(cache_page(60))
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)


class ReviewListAPIView(ListAPIView):
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer
    pagination_class = PageNumberPagination
    lookup_field = "book_id"
    lookup_url_kwarg = "book_id"


class ReviewRateThrottle(UserRateThrottle):
    scope = 'review'


class ReviewCreateAPIView(CreateAPIView):
    serializer_class = ReviewSerializer
    permission_classes = [IsAuthenticated]
    throttle_classes = (ReviewRateThrottle,)


@api_view([HTTPMethod.POST])
@permission_classes([IsAuthenticated])
def like_review(request, review_id):
    review = get_object_or_404(Review, pk=review_id)
    review, _ = ReviewLike.objects.get_or_create(review=review, user=request.user)
    review.is_dislike = False
    review.save()
    return Response(status=status.HTTP_200_OK)


@api_view([HTTPMethod.POST])
@permission_classes([IsAuthenticated])
def dislike_review(request, review_id):
    review = get_object_or_404(Review, pk=review_id)
    review, _ = ReviewLike.objects.get_or_create(review=review, user=request.user)
    review.is_dislike = True
    review.save()
    return Response(status=status.HTTP_200_OK)


@api_view([HTTPMethod.DELETE])
@permission_classes([IsAuthenticated])
def unlike_review(request, review_id):
    review = get_object_or_404(Review, pk=review_id)
    ReviewLike.objects.filter(review=review, user=request.user).delete()
    return Response(status=status.HTTP_204_NO_CONTENT)
