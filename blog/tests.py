from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from django.core.cache import cache
from .models import Post, Category, Tag, Comment, SiteSettings


# ─────────────────────────────────────────
# 모델 테스트
# ─────────────────────────────────────────

class CategoryModelTest(TestCase):
    def setUp(self):
        self.category = Category.objects.create(name='Python', slug='python')

    def test_str(self):
        self.assertEqual(str(self.category), 'Python')

    def test_get_absolute_url(self):
        url = self.category.get_absolute_url()
        self.assertEqual(url, reverse('blog:category', kwargs={'slug': 'python'}))


class TagModelTest(TestCase):
    def setUp(self):
        self.tag = Tag.objects.create(name='Django', slug='django')

    def test_str(self):
        self.assertEqual(str(self.tag), 'Django')


class PostModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='pass1234')
        self.post = Post.objects.create(
            title='테스트 게시글',
            content='내용입니다.',
            author=self.user,
        )

    def test_str(self):
        self.assertEqual(str(self.post), '테스트 게시글')

    def test_get_absolute_url(self):
        url = self.post.get_absolute_url()
        self.assertEqual(url, reverse('blog:post_detail', kwargs={'pk': self.post.pk}))

    def test_default_published(self):
        self.assertTrue(self.post.is_published)

    def test_default_view_count(self):
        self.assertEqual(self.post.view_count, 0)

    def test_ordering_newest_first(self):
        from django.utils import timezone
        import datetime
        post2 = Post.objects.create(title='두 번째', content='내용', author=self.user)
        # created_at이 동일할 수 있으므로 pk 역순으로 보정
        posts = list(Post.objects.order_by('-created_at', '-pk'))
        self.assertEqual(posts[0].pk, post2.pk)


class CommentModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='pass1234')
        self.post = Post.objects.create(title='글', content='내용', author=self.user)
        self.comment = Comment.objects.create(
            post=self.post, author=self.user, content='댓글 내용'
        )

    def test_str(self):
        self.assertIn('testuser', str(self.comment))


class SiteSettingsModelTest(TestCase):
    def tearDown(self):
        cache.clear()

    def test_singleton_pk(self):
        # create() 대신 save()로 호출해야 singleton pk=1 동작
        s1 = SiteSettings(blog_title='블로그1')
        s1.save()
        s2 = SiteSettings(blog_title='블로그2')
        s2.save()
        self.assertEqual(SiteSettings.objects.count(), 1)
        self.assertEqual(SiteSettings.objects.get().blog_title, '블로그2')

    def test_get_settings_caches(self):
        SiteSettings.objects.create(blog_title='캐시테스트')
        s = SiteSettings.get_settings()
        self.assertEqual(s.blog_title, '캐시테스트')
        cached = cache.get('site_settings')
        self.assertIsNotNone(cached)

    def test_save_clears_cache(self):
        s = SiteSettings.objects.create(blog_title='초기값')
        SiteSettings.get_settings()  # 캐시에 저장
        s.blog_title = '변경값'
        s.save()
        self.assertIsNone(cache.get('site_settings'))


# ─────────────────────────────────────────
# 뷰 테스트
# ─────────────────────────────────────────

class PostListViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='pass1234')
        Post.objects.create(title='공개글', content='내용', author=self.user, is_published=True)
        Post.objects.create(title='비공개글', content='내용', author=self.user, is_published=False)

    def test_list_shows_only_published(self):
        response = self.client.get(reverse('blog:post_list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, '공개글')
        self.assertNotContains(response, '비공개글')

    def test_search_by_title(self):
        response = self.client.get(reverse('blog:post_list'), {'q': '공개'})
        self.assertContains(response, '공개글')

    def test_search_no_result(self):
        response = self.client.get(reverse('blog:post_list'), {'q': '없는글제목xyz'})
        self.assertEqual(len(response.context['posts']), 0)


class PostDetailViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='pass1234')
        self.post = Post.objects.create(
            title='상세글', content='내용', author=self.user, is_published=True
        )
        self.hidden = Post.objects.create(
            title='숨김글', content='내용', author=self.user, is_published=False
        )

    def test_view_count_increments(self):
        self.client.get(reverse('blog:post_detail', kwargs={'pk': self.post.pk}))
        self.post.refresh_from_db()
        self.assertEqual(self.post.view_count, 1)

    def test_hidden_post_returns_404(self):
        response = self.client.get(reverse('blog:post_detail', kwargs={'pk': self.hidden.pk}))
        self.assertEqual(response.status_code, 404)


class CategoryViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='pass1234')
        self.category = Category.objects.create(name='Python', slug='python')
        Post.objects.create(title='Python글', content='내용', author=self.user,
                            category=self.category, is_published=True)
        Post.objects.create(title='기타글', content='내용', author=self.user, is_published=True)

    def test_category_filter(self):
        response = self.client.get(reverse('blog:category', kwargs={'slug': 'python'}))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Python글')
        self.assertNotContains(response, '기타글')

    def test_invalid_category_404(self):
        response = self.client.get(reverse('blog:category', kwargs={'slug': 'nonexistent'}))
        self.assertEqual(response.status_code, 404)


class TagViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='pass1234')
        self.tag = Tag.objects.create(name='Django', slug='django')
        post = Post.objects.create(title='Django글', content='내용', author=self.user, is_published=True)
        post.tags.add(self.tag)
        Post.objects.create(title='태그없음', content='내용', author=self.user, is_published=True)

    def test_tag_filter(self):
        response = self.client.get(reverse('blog:tag', kwargs={'slug': 'django'}))
        self.assertContains(response, 'Django글')
        self.assertNotContains(response, '태그없음')


class PostCreateViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='pass1234')

    def test_redirect_if_not_logged_in(self):
        response = self.client.get(reverse('blog:post_create'))
        self.assertNotEqual(response.status_code, 200)

    def test_create_post_logged_in(self):
        self.client.login(username='testuser', password='pass1234')
        response = self.client.post(reverse('blog:post_create'), {
            'title': '새 게시글',
            'content': '내용입니다.',
            'is_published': True,
        })
        self.assertEqual(Post.objects.filter(title='새 게시글').count(), 1)
        post = Post.objects.get(title='새 게시글')
        self.assertEqual(post.author, self.user)
        self.assertRedirects(response, post.get_absolute_url())

    def test_author_set_to_current_user(self):
        self.client.login(username='testuser', password='pass1234')
        self.client.post(reverse('blog:post_create'), {
            'title': '작성자확인',
            'content': '내용',
            'is_published': True,
        })
        post = Post.objects.get(title='작성자확인')
        self.assertEqual(post.author, self.user)


class PostEditViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.owner = User.objects.create_user(username='owner', password='pass1234')
        self.other = User.objects.create_user(username='other', password='pass1234')
        self.post = Post.objects.create(title='원본제목', content='내용', author=self.owner)

    def test_owner_can_edit(self):
        self.client.login(username='owner', password='pass1234')
        response = self.client.post(
            reverse('blog:post_edit', kwargs={'pk': self.post.pk}),
            {'title': '수정제목', 'content': '수정내용', 'is_published': True},
        )
        self.post.refresh_from_db()
        self.assertEqual(self.post.title, '수정제목')

    def test_other_user_cannot_edit(self):
        self.client.login(username='other', password='pass1234')
        response = self.client.get(reverse('blog:post_edit', kwargs={'pk': self.post.pk}))
        self.assertEqual(response.status_code, 404)


class PostDeleteViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.owner = User.objects.create_user(username='owner', password='pass1234')
        self.other = User.objects.create_user(username='other', password='pass1234')
        self.post = Post.objects.create(title='삭제대상', content='내용', author=self.owner)

    def test_owner_can_delete(self):
        self.client.login(username='owner', password='pass1234')
        self.client.post(reverse('blog:post_delete', kwargs={'pk': self.post.pk}))
        self.assertEqual(Post.objects.filter(pk=self.post.pk).count(), 0)

    def test_delete_redirects_to_list(self):
        self.client.login(username='owner', password='pass1234')
        response = self.client.post(reverse('blog:post_delete', kwargs={'pk': self.post.pk}))
        self.assertRedirects(response, reverse('blog:post_list'))

    def test_other_user_cannot_delete(self):
        self.client.login(username='other', password='pass1234')
        response = self.client.post(reverse('blog:post_delete', kwargs={'pk': self.post.pk}))
        self.assertEqual(Post.objects.filter(pk=self.post.pk).count(), 1)


class CommentCreateViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='pass1234')
        self.post = Post.objects.create(title='글', content='내용', author=self.user)

    def test_comment_requires_login(self):
        response = self.client.post(
            reverse('blog:comment_create', kwargs={'pk': self.post.pk}),
            {'content': '댓글'}
        )
        self.assertEqual(Comment.objects.count(), 0)

    def test_logged_in_user_can_comment(self):
        self.client.login(username='testuser', password='pass1234')
        self.client.post(
            reverse('blog:comment_create', kwargs={'pk': self.post.pk}),
            {'content': '댓글 내용'}
        )
        self.assertEqual(Comment.objects.count(), 1)
        self.assertEqual(Comment.objects.first().author, self.user)


class CommentDeleteViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.owner = User.objects.create_user(username='owner', password='pass1234')
        self.other = User.objects.create_user(username='other', password='pass1234')
        self.post = Post.objects.create(title='글', content='내용', author=self.owner)
        self.comment = Comment.objects.create(
            post=self.post, author=self.owner, content='삭제할 댓글'
        )

    def test_owner_can_delete_comment(self):
        self.client.login(username='owner', password='pass1234')
        self.client.post(reverse('blog:comment_delete', kwargs={
            'pk': self.post.pk, 'comment_pk': self.comment.pk
        }))
        self.assertEqual(Comment.objects.count(), 0)

    def test_other_user_cannot_delete_comment(self):
        self.client.login(username='other', password='pass1234')
        self.client.post(reverse('blog:comment_delete', kwargs={
            'pk': self.post.pk, 'comment_pk': self.comment.pk
        }))
        self.assertEqual(Comment.objects.count(), 1)


# ─────────────────────────────────────────
# 인증 테스트
# ─────────────────────────────────────────

class AuthTest(TestCase):
    def setUp(self):
        self.client = Client()
        User.objects.create_user(username='admin', password='adminpass')

    def test_login_success(self):
        response = self.client.post('/accounts/login/', {
            'username': 'admin', 'password': 'adminpass'
        }, follow=True)
        self.assertTrue(response.context['user'].is_authenticated)

    def test_login_failure(self):
        response = self.client.post('/accounts/login/', {
            'username': 'admin', 'password': 'wrongpass'
        }, follow=True)
        self.assertFalse(response.context['user'].is_authenticated)

    def test_logout(self):
        self.client.login(username='admin', password='adminpass')
        self.client.post('/accounts/logout/')
        response = self.client.get(reverse('blog:post_list'))
        self.assertFalse(response.wsgi_request.user.is_authenticated)
