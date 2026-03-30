import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.contrib.auth import get_user_model
from blog.models import Category, Tag, Post

User = get_user_model()
admin = User.objects.get(username='admin')

Category.objects.all().delete()
Tag.objects.all().delete()

cat1 = Category.objects.create(name='일상', slug='daily')
cat2 = Category.objects.create(name='기술', slug='tech')
cat3 = Category.objects.create(name='여행', slug='travel')

tag1 = Tag.objects.create(name='Python', slug='python')
tag2 = Tag.objects.create(name='Django', slug='django')
tag3 = Tag.objects.create(name='개발', slug='dev')

Post.objects.all().delete()

p1 = Post.objects.create(
    title='Django로 블로그를 만들었습니다',
    content='안녕하세요! 커서 AI가 Django 6.0.3으로 블로그 시스템을 만들어줬습니다.\n\nDjango는 Python 기반의 웹 프레임워크로, 빠르고 안정적인 웹 개발이 가능합니다.\n\n이 블로그에서는 카테고리, 태그, 댓글 기능을 모두 사용할 수 있습니다.\n\n글쓰기 버튼을 눌러 직접 게시글을 작성해보세요!',
    author=admin,
    category=cat2,
)
p1.tags.add(tag1, tag2, tag3)

p2 = Post.objects.create(
    title='첫 번째 일상 기록',
    content='오늘은 날씨가 정말 좋았습니다.\n\n커피 한 잔 마시며 코딩하는 하루였는데, 생각보다 많은 것들을 만들어냈습니다.\n\n앞으로도 꾸준히 기록해나가겠습니다.',
    author=admin,
    category=cat1,
)

p3 = Post.objects.create(
    title='서울 도심 여행기',
    content='서울의 숨겨진 골목골목을 탐험했습니다.\n\n경복궁 근처의 작은 카페에서 여유를 즐겼고, 북촌 한옥마을을 걸으며 전통의 아름다움을 느꼈습니다.\n\n다음에는 부산으로 떠나볼 계획입니다.',
    author=admin,
    category=cat3,
)

print('샘플 데이터 생성 완료!')
print(f'카테고리: {Category.objects.count()}개')
print(f'태그: {Tag.objects.count()}개')
print(f'게시글: {Post.objects.count()}개')
