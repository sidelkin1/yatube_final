import itertools

from django import forms
from django.contrib.auth import get_user_model
from django.db import models
from django.forms import ModelForm

from .models import RATING_CHOICES, Comment, Group, Post

User = get_user_model()


class PostForm(ModelForm):
    """Форма добавления/редактирования постов."""
    class Meta:
        model = Post
        fields = ('text', 'group', 'image')
        widgets = {
            'text': forms.Textarea(
                attrs={'placeholder': 'Текст поста...'}
            ),
        }


class CommentForm(ModelForm):
    """Форма добавления комментария."""
    class Meta:
        model = Comment
        fields = ('text',)
        widgets = {
            'text': forms.Textarea(
                attrs={'placeholder': 'Текст комментария...'}
            ),
        }


class RatingForm(forms.Form):
    """Форма добавления рейтинга."""
    rating = forms.ChoiceField(
        label='Рейтинг',
        required=False,
        choices=itertools.chain(
            ((None, '-пусто-'),),
            RATING_CHOICES
        ),
    )


class AuthorModelChoiceField(forms.ModelChoiceField):
    def label_from_instance(self, obj):
        return obj.get_full_name() or obj.username


class PostFilterForm(forms.Form):
    """Форма для фильтрации на главной странице."""
    author = AuthorModelChoiceField(
        label='Автор',
        required=False,
        empty_label=None,
        queryset=User.objects.annotate(
            post_count=models.Count('posts')
        ).filter(post_count__gt=0),
    )

    group = forms.ModelChoiceField(
        label='Группа',
        required=False,
        empty_label=None,
        queryset=Group.objects.annotate(
            post_count=models.Count('posts')
        ).filter(post_count__gt=0),
    )

    rating = forms.ChoiceField(
        label='Рейтинг',
        required=False,
        choices=RATING_CHOICES,
    )
