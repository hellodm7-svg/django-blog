from django.contrib import admin
from django_summernote.admin import SummernoteModelAdmin
from .models import Post, Category, Tag, Comment, SiteSettings


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug']
    prepopulated_fields = {'slug': ('name',)}


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug']
    prepopulated_fields = {'slug': ('name',)}


@admin.register(Post)
class PostAdmin(SummernoteModelAdmin):
    summernote_fields = ('content',)
    list_display = ['title', 'author', 'category', 'is_published', 'view_count', 'created_at']
    list_filter = ['is_published', 'category', 'created_at']
    search_fields = ['title', 'content']
    raw_id_fields = ['author']
    date_hierarchy = 'created_at'
    ordering = ['-created_at']


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ['author', 'post', 'created_at']
    list_filter = ['created_at']
    search_fields = ['content']


@admin.register(SiteSettings)
class SiteSettingsAdmin(admin.ModelAdmin):
    fieldsets = (
        ('🎨 테마 설정', {
            'fields': ('theme',),
            'description': '블로그 전체 테마를 선택하세요. 저장 즉시 적용됩니다.',
        }),
        ('📝 블로그 정보', {
            'fields': ('blog_title', 'blog_description'),
        }),
    )

    def has_add_permission(self, request):
        return not SiteSettings.objects.exists()

    def has_delete_permission(self, request, obj=None):
        return False
