from django.contrib import admin

from posts.models import Comment, Follow, Group, Post
from yatube.admin import BaseAdmin


@admin.register(Post)
class PostAdmin(BaseAdmin):
    list_display = ('pk', 'text', 'pub_date', 'author', 'group')
    list_editable = ('group',)
    search_fields = ('text',)
    list_filter = ('pub_date',)


@admin.register(Group)
class GroupAdmin(BaseAdmin):
    list_display = ('pk', 'title', 'slug', 'description')
    search_fields = ('title',)
    slug = ('slug',)
    description = ('description',)


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('pk', 'author', 'post', 'pub_date')
    list_filter = ('pub_date',)
    search_fields = ('text', 'author__username', 'post__text')


@admin.register(Follow)
class FollowAdmin(admin.ModelAdmin):
    list_display = ('pk', 'user', 'author')
    list_filter = ('user', 'author')
    search_fields = ('user__username', 'author__username')
