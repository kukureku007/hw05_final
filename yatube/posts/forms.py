from django import forms

from .models import Comment, Post


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = (
            'text',
            'group',
            'image'
        )


class СommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = (
            'text',
            # 'post'  # возможно тут будет ошибка
        )
