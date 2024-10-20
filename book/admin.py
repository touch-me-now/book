from django.contrib import admin

from book.models import Category, Book, Review, ReviewReaction


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("slug", "title")
    search_fields = ("slug", "title",)
    prepopulated_fields = {'slug': ('title',), }
    list_per_page = 10


@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    autocomplete_fields = ("category",)
    list_display = ("id", "title", "category", "rating")
    list_filter = ("rating",)
    search_fields = ("id", "title",)
    list_per_page = 10


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    autocomplete_fields = ("book", "user")
    list_display = ("id", "user", "book", "rating", "created_at", "reactions")
    list_filter = ("rating", "created_at",)
    search_fields = ("book__title", "user__username",)
    list_per_page = 10

    @admin.display(description='Reactions')
    def reactions(self, obj) -> int:
        return obj.reacts.count()


@admin.register(ReviewReaction)
class ReviewReactionAdmin(admin.ModelAdmin):
    autocomplete_fields = ("review", "user")
    list_display = ("id", "review", "user", "reaction", "created_at", "updated_at")
    list_filter = ("created_at", "updated_at")
    list_per_page = 10

    @admin.display(description='Reactions')
    def reactions(self, obj) -> int:
        return obj.reacts.count()
