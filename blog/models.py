from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse


class Category(models.Model):
    name = models.CharField(max_length=100, unique=True, verbose_name='카테고리명')
    slug = models.SlugField(max_length=100, unique=True, allow_unicode=True)

    class Meta:
        verbose_name = '카테고리'
        verbose_name_plural = '카테고리 목록'

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('blog:category', kwargs={'slug': self.slug})


class Tag(models.Model):
    name = models.CharField(max_length=50, unique=True, verbose_name='태그명')
    slug = models.SlugField(max_length=50, unique=True, allow_unicode=True)

    class Meta:
        verbose_name = '태그'
        verbose_name_plural = '태그 목록'

    def __str__(self):
        return self.name


class Post(models.Model):
    title = models.CharField(max_length=200, verbose_name='제목')
    content = models.TextField(verbose_name='내용')
    thumbnail = models.ImageField(upload_to='blog/thumbnails/', blank=True, null=True, verbose_name='썸네일')
    author = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='작성자')
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True, verbose_name='카테고리')
    tags = models.ManyToManyField(Tag, blank=True, verbose_name='태그')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='작성일')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='수정일')
    is_published = models.BooleanField(default=True, verbose_name='공개 여부')
    view_count = models.PositiveIntegerField(default=0, verbose_name='조회수')

    class Meta:
        verbose_name = '게시글'
        verbose_name_plural = '게시글 목록'
        ordering = ['-created_at']

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('blog:post_detail', kwargs={'pk': self.pk})


class SiteSettings(models.Model):
    THEME_CHOICES = [
        ('dark',      '🌑 다크 (GitHub Dark)'),
        ('light',     '☀️ 라이트 모던'),
        ('magazine',  '📰 매거진 (신문 스타일)'),
        ('minimal',   '⬜ 미니멀 화이트'),
    ]
    theme = models.CharField(
        max_length=20,
        choices=THEME_CHOICES,
        default='dark',
        verbose_name='블로그 테마'
    )
    blog_title = models.CharField(max_length=100, default='My Blog', verbose_name='블로그 제목')
    blog_description = models.CharField(max_length=200, default='생각을 기록하는 공간', verbose_name='블로그 설명')

    class Meta:
        verbose_name = '사이트 설정'
        verbose_name_plural = '사이트 설정'

    def __str__(self):
        return f'사이트 설정 (테마: {self.get_theme_display()})'

    def save(self, *args, **kwargs):
        self.pk = 1
        super().save(*args, **kwargs)

    @classmethod
    def get_settings(cls):
        obj, _ = cls.objects.get_or_create(pk=1)
        return obj


class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments', verbose_name='게시글')
    author = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='작성자')
    content = models.TextField(verbose_name='내용')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='작성일')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='수정일')

    class Meta:
        verbose_name = '댓글'
        verbose_name_plural = '댓글 목록'
        ordering = ['created_at']

    def __str__(self):
        return f'{self.author} - {self.post.title[:20]}'
