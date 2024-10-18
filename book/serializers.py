from django.db.models import Count, Q
from rest_framework import serializers

from book.models import Book, Category, Review
from book.utils import update_book_rating


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ("title", "slug")


class BookSerializer(serializers.ModelSerializer):
    category = CategorySerializer(many=False, read_only=True)

    class Meta:
        model = Book
        fields = ("id", "title", "author", "description", "cover_img", "rating", "category")


class ReviewSerializer(serializers.ModelSerializer):
    author_name = serializers.SerializerMethodField(read_only=True)
    book = serializers.PrimaryKeyRelatedField(
        queryset=Book.objects.all(),
        write_only=True,
        required=True
    )
    likes = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Review
        fields = ("id", "book", "author_name", "comment", "rating", "created_at", "likes")

    def get_author_name(self, obj):
        return obj.user.username

    def get_likes(self, obj):
        return obj.likes.aggregate(
            likes=Count("id", filter=Q(is_dislike=False)),
            dislikes=Count("id", filter=Q(is_dislike=True))
        )

    def validate(self, attrs):
        request = self.context["request"]
        attrs["user"] = request.user
        return attrs

    def create(self, validated_data):
        instance = super().create(validated_data)
        update_book_rating(instance.book)
        return instance
