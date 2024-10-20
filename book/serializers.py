from django.utils.translation import gettext_lazy as _
from drf_spectacular.utils import extend_schema_serializer
from rest_framework import serializers

from book.models import Book, Category, Review, ReviewReaction


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ("title", "slug")


class BookSerializer(serializers.ModelSerializer):
    category = CategorySerializer(many=False, read_only=True)

    class Meta:
        model = Book
        fields = ("id", "title", "author", "cover_img", "rating", "category")


class BookDetailSerializer(serializers.ModelSerializer):
    category = CategorySerializer(many=False, read_only=True)
    reviews = serializers.HyperlinkedRelatedField(
        many=True,
        read_only=True,
        view_name="book-reviews-list",
        lookup_url_kwarg="book_id",
    )

    class Meta:
        model = Book
        fields = ("id", "title", "author", "description", "cover_img", "rating", "category", "reviews")



class ReactionCountListField(serializers.ListSerializer):
    def __init__(self, *args, **kwargs):
        kwargs["child"] = serializers.JSONField()
        kwargs["read_only"] = True

        self.choices = {v: l for v, l in ReviewReaction.Reaction.choices}
        super().__init__(*args, **kwargs)

    def represent_reaction(self, value):
        if "reaction" in value:
            reaction_value = value["reaction"]
            value["reaction"] = self.choices.get(reaction_value, reaction_value)
        return value

    def to_representation(self, data):
        return [
            self.represent_reaction(value) for value in super().to_representation(data) if value
        ] or None


class ReviewSerializer(serializers.ModelSerializer):
    book = serializers.PrimaryKeyRelatedField(
        queryset=Book.objects.all(),
        write_only=True,
        required=True
    )
    reactions = ReactionCountListField()

    class Meta:
        model = Review
        fields = ("id", "book", "author", "comment", "rating", "created_at", "reactions")

    def validate(self, attrs):
        request = self.context["request"]
        attrs["user"] = request.user
        return attrs


@extend_schema_serializer(exclude_fields=('review',))
class ReviewReactionSerializer(serializers.ModelSerializer):
    review = serializers.PrimaryKeyRelatedField(
        queryset=Review.objects.all(),
        write_only=True,
        required=True,
    )
    reaction = serializers.ChoiceField(
        choices=ReviewReaction.Reaction.choices,
        write_only=True,
        required=True,
    )

    class Meta:
        model = ReviewReaction
        fields = ("review", "reaction")

    def validate(self, attrs):
        if self.instance:  # to avoid sending user when updating
            return attrs

        user = self.context["request"].user

        if ReviewReaction.objects.filter(user=user, review=attrs["review"]).exists():
            raise serializers.ValidationError({"detail": _('Already exists! Try update')})
        attrs["user"] = user
        return attrs
