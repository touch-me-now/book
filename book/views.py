from http import HTTPMethod

from django.core.exceptions import ValidationError as DjangoValidationError
from django.core.validators import validate_slug
from django.http import Http404
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.decorators import permission_classes, api_view
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from rest_framework.generics import ListAPIView, CreateAPIView, UpdateAPIView, DestroyAPIView
from rest_framework.filters import BaseFilterBackend, SearchFilter
from rest_framework.permissions import IsAuthenticated, BasePermission
from rest_framework.viewsets import ReadOnlyModelViewSet
from rest_framework.pagination import PageNumberPagination

from book.models import Book, Review, ReviewReaction
from book.serializers import BookSerializer, ReviewSerializer, ReviewReactionSerializer, BookDetailSerializer
from book.throttles import ReviewRateThrottle, ReactionRateThrottle


class BookCategoryFilter(BaseFilterBackend):
    category_param = "category"

    def filter_queryset(self, request, queryset, view):
        category_value = request.query_params.get(self.category_param, '')
        if category_value.strip():

            try:
                validate_slug(category_value)
            except DjangoValidationError as err:
                raise ValidationError(detail=err.args[0])

            return queryset.filter(category__slug=category_value)
        return queryset


class BookViewSet(ReadOnlyModelViewSet):
    queryset = Book.objects.select_related("category").all()
    serializer_class = BookSerializer
    retrieve_serializer_class = BookDetailSerializer
    pagination_class = PageNumberPagination
    filter_backends = (BookCategoryFilter, SearchFilter)
    search_fields = ["title"]
    lookup_url_kwarg = "book_id"
    lookup_field = "id"

    def get_serializer_class(self):
        if self.request.method == 'GET' and self.lookup_url_kwarg in self.kwargs:
            return self.retrieve_serializer_class
        return super().get_serializer_class()

    @method_decorator(cache_page(60))
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)


class ReviewListAPIView(ListAPIView):
    queryset = Review.objects.reviews_with_reactions()
    serializer_class = ReviewSerializer
    pagination_class = PageNumberPagination
    lookup_field = "book_id"
    lookup_url_kwarg = "book_id"


class ReviewCreateAPIView(CreateAPIView):
    serializer_class = ReviewSerializer
    permission_classes = [IsAuthenticated]
    throttle_classes = (ReviewRateThrottle,)


class IsAuthor(BasePermission):
    def has_object_permission(self, request, view, obj):
        return request.user.id == obj.user_id


class ReviewDestroyAPIView(DestroyAPIView):
    queryset = Review.objects.all()
    permission_classes = [IsAuthenticated, IsAuthor]


class ReviewReactionAPIView(
    CreateAPIView,
    UpdateAPIView,
    DestroyAPIView
):
    queryset = ReviewReaction.objects.all()
    serializer_class = ReviewReactionSerializer
    permission_classes = [IsAuthenticated, IsAuthor]
    throttle_classes = (ReactionRateThrottle,)
    lookup_url_kwarg = "review_id"
    lookup_field = "review_id"

    def get_queryset(self):
        return super().get_queryset().filter(user=self.request.user)

    def create(self, request, *args, **kwargs):
        request.data["review"] = kwargs["review_id"]
        return super().create(request, *args, **kwargs)


class ReviewReactionCreateAPIView(CreateAPIView):
    serializer_class = ReviewReactionSerializer
    permission_classes = [IsAuthenticated]
    throttle_classes = (ReactionRateThrottle,)


class ReviewReactionUpdateAPIView(UpdateAPIView):
    queryset = ReviewReaction.objects.all()
    serializer_class = ReviewReactionSerializer
    permission_classes = [IsAuthenticated]
    throttle_classes = (ReactionRateThrottle,)

    def get_queryset(self):
        return super().get_queryset().filter(user=self.request.user)


@extend_schema(responses={status.HTTP_204_NO_CONTENT: None, status.HTTP_404_NOT_FOUND: "Review reaction not found"})
@api_view([HTTPMethod.DELETE])
@permission_classes([IsAuthenticated])
def review_reaction_cancel_view(request, review_id):
    react = ReviewReaction.objects.filter(review_id=review_id, user=request.user)
    if not react.exists():
        raise Http404("Review reaction not found")
    return Response(status=status.HTTP_204_NO_CONTENT)
