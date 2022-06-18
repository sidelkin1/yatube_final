from django.contrib import admin

from .models import Comment, Follow, Group, Post, Rating


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    """Представление модели поста в админке."""

    list_display = ('pk', 'text', 'pub_date', 'author', 'group', 'image')
    search_fields = ('text',)
    list_filter = ('pub_date',)
    empty_value_display = '-пусто-'
    list_editable = ('group',)


@admin.register(Group)
class GroupAdmin(admin.ModelAdmin):
    """Представление модели группы в админке."""

    list_display = ('title', 'slug', 'description')
    prepopulated_fields = {'slug': ('title',)}
    search_fields = ('description',)
    empty_value_display = '-пусто-'


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    """Представление модели поста в админке."""

    list_display = ('pk', 'post', 'author', 'text')
    search_fields = ('text',)
    list_filter = ('created',)
    empty_value_display = '-пусто-'
    list_editable = ('post', 'author')


@admin.register(Follow)
class FollowAdmin(admin.ModelAdmin):
    """Представление модели поста в админке."""

    list_display = ('pk', 'user', 'author')
    list_editable = ('user', 'author')


@admin.register(Rating)
class RatingAdmin(admin.ModelAdmin):
    """Представление модели поста в админке."""

    list_display = ('pk', 'user', 'post', 'rating')
    list_editable = ('user', 'post', 'rating')
