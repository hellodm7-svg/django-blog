from django import forms
from django_summernote.widgets import SummernoteWidget
from .models import Post, Comment


class PostForm(forms.ModelForm):
    def __init__(self, *args, use_simple_editor=False, **kwargs):
        super().__init__(*args, **kwargs)
        if use_simple_editor:
            self.fields['content'].widget = forms.Textarea(attrs={
                'class': 'form-control memo-editor',
                'rows': 20,
                'placeholder': '내용을 입력하세요',
                'autocomplete': 'off',
                'autocapitalize': 'sentences',
                'autocorrect': 'on',
            })
        else:
            self.fields['content'].widget = SummernoteWidget()

    class Meta:
        model = Post
        fields = ['title', 'content', 'thumbnail', 'category', 'tags', 'is_published']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '제목을 입력하세요'}),
            'thumbnail': forms.ClearableFileInput(attrs={'class': 'form-control'}),
            'category': forms.Select(attrs={'class': 'form-select'}),
            'tags': forms.CheckboxSelectMultiple(),
            'is_published': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
        labels = {
            'title': '제목',
            'content': '내용',
            'thumbnail': '썸네일 이미지',
            'category': '카테고리',
            'tags': '태그',
            'is_published': '공개',
        }


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['content']
        widgets = {
            'content': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': '댓글을 입력하세요',
            }),
        }
        labels = {
            'content': '',
        }
