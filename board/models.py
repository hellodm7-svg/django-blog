from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse


class Category(models.Model):
    name = models.CharField(max_length=50, unique=True)

    class Meta:
        verbose_name = '카테고리'
        verbose_name_plural = '카테고리'

    def __str__(self):
        return self.name


class BoardPost(models.Model):
    title      = models.CharField(max_length=200, verbose_name='제목')
    content    = models.TextField(verbose_name='내용')
    author     = models.ForeignKey(User, on_delete=models.CASCADE, related_name='board_posts', verbose_name='작성자')
    category   = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True, verbose_name='카테고리')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='작성일')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='수정일')
    view_count = models.PositiveIntegerField(default=0, verbose_name='조회수')

    class Meta:
        ordering = ['-created_at']
        verbose_name = '게시글'
        verbose_name_plural = '게시글'

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('board:post_detail', kwargs={'pk': self.pk})


class Comment(models.Model):
    post       = models.ForeignKey(BoardPost, on_delete=models.CASCADE, related_name='comments', verbose_name='게시글')
    author     = models.ForeignKey(User, on_delete=models.CASCADE, related_name='board_comments', verbose_name='작성자')
    content    = models.TextField(verbose_name='내용')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='작성일')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='수정일')

    class Meta:
        ordering = ['created_at']
        verbose_name = '댓글'
        verbose_name_plural = '댓글'

    def __str__(self):
        return f'{self.author.username}: {self.content[:30]}'
