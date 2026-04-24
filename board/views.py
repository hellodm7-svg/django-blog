from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q
from django.http import HttpResponseForbidden
from .models import BoardPost, Comment, Category
from .forms import BoardPostForm, CommentForm


def post_list(request):
    posts = BoardPost.objects.select_related('author', 'category').all()
    query = request.GET.get('q')
    category_id = request.GET.get('category')

    if query:
        posts = posts.filter(
            Q(title__icontains=query) | Q(content__icontains=query)
        )
    if category_id:
        posts = posts.filter(category_id=category_id)

    paginator = Paginator(posts, 10)
    page = request.GET.get('page')
    posts = paginator.get_page(page)

    categories = Category.objects.all()
    return render(request, 'board/post_list.html', {
        'posts': posts,
        'categories': categories,
        'query': query,
        'current_category_id': int(category_id) if category_id else None,
    })


def post_detail(request, pk):
    post = get_object_or_404(BoardPost, pk=pk)
    post.view_count += 1
    post.save(update_fields=['view_count'])
    comments = post.comments.select_related('author').all()
    comment_form = CommentForm()
    return render(request, 'board/post_detail.html', {
        'post': post,
        'comments': comments,
        'comment_form': comment_form,
    })


@login_required
def post_create(request):
    if request.method == 'POST':
        form = BoardPostForm(request.POST)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()
            messages.success(request, '게시글이 작성되었습니다.')
            return redirect(post.get_absolute_url())
    else:
        form = BoardPostForm()
    return render(request, 'board/post_form.html', {'form': form, 'action': '작성'})


@login_required
def post_edit(request, pk):
    post = get_object_or_404(BoardPost, pk=pk)
    if request.user != post.author:
        return HttpResponseForbidden('수정 권한이 없습니다.')
    if request.method == 'POST':
        form = BoardPostForm(request.POST, instance=post)
        if form.is_valid():
            form.save()
            messages.success(request, '게시글이 수정되었습니다.')
            return redirect(post.get_absolute_url())
    else:
        form = BoardPostForm(instance=post)
    return render(request, 'board/post_form.html', {'form': form, 'action': '수정', 'post': post})


@login_required
def post_delete(request, pk):
    post = get_object_or_404(BoardPost, pk=pk)
    if request.user != post.author:
        return HttpResponseForbidden('삭제 권한이 없습니다.')
    if request.method == 'POST':
        post.delete()
        messages.success(request, '게시글이 삭제되었습니다.')
        return redirect('board:post_list')
    return render(request, 'board/post_confirm_delete.html', {'post': post})


@login_required
def comment_create(request, pk):
    post = get_object_or_404(BoardPost, pk=pk)
    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.post = post
            comment.author = request.user
            comment.save()
            messages.success(request, '댓글이 작성되었습니다.')
    return redirect(post.get_absolute_url())


@login_required
def comment_edit(request, pk, comment_pk):
    comment = get_object_or_404(Comment, pk=comment_pk)
    if request.user != comment.author:
        return HttpResponseForbidden('수정 권한이 없습니다.')
    if request.method == 'POST':
        form = CommentForm(request.POST, instance=comment)
        if form.is_valid():
            form.save()
            messages.success(request, '댓글이 수정되었습니다.')
            return redirect('board:post_detail', pk=comment.post.pk)
    else:
        form = CommentForm(instance=comment)
    return render(request, 'board/comment_form.html', {'form': form, 'comment': comment})


@login_required
def comment_delete(request, pk, comment_pk):
    comment = get_object_or_404(Comment, pk=comment_pk)
    if request.user != comment.author:
        return HttpResponseForbidden('삭제 권한이 없습니다.')
    if request.method == 'POST':
        post_pk = comment.post.pk
        comment.delete()
        messages.success(request, '댓글이 삭제되었습니다.')
        return redirect('board:post_detail', pk=post_pk)
    return redirect('board:post_detail', pk=pk)
