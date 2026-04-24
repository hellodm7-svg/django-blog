from django.contrib import admin
from unfold.admin import ModelAdmin, TabularInline
from .models import BoardPost, Comment, Category


@admin.register(Category)
class CategoryAdmin(ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)


class CommentInline(TabularInline):
    model = Comment
    extra = 1
    fields = ('author', 'content', 'created_at')
    readonly_fields = ('created_at',)


@admin.register(BoardPost)
class BoardPostAdmin(ModelAdmin):
    list_display  = ('title', 'author', 'category', 'view_count', 'created_at')
    list_filter   = ('created_at', 'author', 'category')
    search_fields = ('title', 'content')
    inlines       = [CommentInline]


@admin.register(Comment)
class CommentAdmin(ModelAdmin):
    list_display  = ('author', 'content', 'post', 'created_at')
    list_filter   = ('created_at', 'author')
    search_fields = ('content', 'author__username')
