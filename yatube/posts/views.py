import contextlib

from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db import IntegrityError, transaction
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.views.generic import DeleteView

from .forms import CommentForm, PostFilterForm, PostForm, RatingForm
from .models import Follow, Group, Post, Rating
from .utils import create_facets, filter_facets, get_page_obj, query_posts

User = get_user_model()


class LockedView(LoginRequiredMixin):
    login_url = 'users:login'


def index(request):
    """Главная страница с постами."""

    posts = query_posts(Post.objects)
    form = PostFilterForm(data=request.GET)
    facets = create_facets(form)
    if form.is_valid():
        posts = filter_facets(facets, posts, form)
    page_obj = get_page_obj(request.GET.get('page'), list(posts))

    context = {
        'form': form,
        'facets': facets,
        'page_obj': page_obj,
    }
    return render(request, 'posts/index.html', context)


def group_posts(request, slug):
    """Выборочные посты по группе."""

    group = get_object_or_404(Group, slug=slug)
    posts = query_posts(group.posts)
    page_obj = get_page_obj(request.GET.get('page'), list(posts))

    context = {
        'group': group,
        'page_obj': page_obj,
    }
    return render(request, 'posts/group_list.html', context)


def profile(request, username):
    """Профиль пользователя."""

    author = get_object_or_404(User, username=username)
    posts = query_posts(author.posts)
    user = request.user
    following = (
        user.is_authenticated
        and Follow.objects.filter(user=user, author=author).exists()
    )
    page_obj = get_page_obj(request.GET.get('page'), list(posts))

    context = {
        'author': author,
        'page_obj': page_obj,
        'following': following,
    }
    return render(request, 'posts/profile.html', context)


def post_detail(request, post_id):
    """Детальное описание поста."""

    queryset = query_posts(Post.objects)
    post = get_object_or_404(queryset, pk=post_id)
    comments = post.comments.select_related('author')

    context = {
        'post': post,
        'form_comment': CommentForm(),
        'comments': comments,
        'form_rating': RatingForm(),
    }
    return render(request, 'posts/post_detail.html', context)


@login_required
def post_create(request):
    """Создание нового поста."""

    form = PostForm(
        data=request.POST or None,
        files=request.FILES or None
    )
    if form.is_valid():
        post = form.save(commit=False)
        post.author = request.user
        post.save()
        return redirect('posts:profile', username=request.user.username)

    context = {
        'form': form,
        'is_edit': False,
    }
    return render(request, 'posts/create_post.html', context)


@login_required
def post_edit(request, post_id):
    """Редактирование старого поста."""

    queryset = Post.objects.select_related('author')
    post = get_object_or_404(queryset, pk=post_id)

    # Только автор поста может его редактировать
    if request.user != post.author:
        return redirect('posts:post_detail', post_id=post_id)

    form = PostForm(
        data=request.POST or None,
        files=request.FILES or None,
        instance=post
    )
    if form.is_valid():
        post = form.save(commit=False)
        post.save(update_fields=['text', 'group', 'image'])
        return redirect('posts:post_detail', post_id=post_id)

    context = {
        'form': form,
        'is_edit': True,
    }
    return render(request, 'posts/create_post.html', context)


class PostDeleteView(LockedView, DeleteView):
    """Удаление постов."""

    model = Post
    pk_url_kwarg = 'post_id'
    success_url = reverse_lazy('posts:index')
    queryset = Post.objects.select_related('author')

    def dispatch(self, request, *args, **kwargs):
        """Только автор поста может удалить его."""
        if request.user.is_authenticated:
            post_id = self.kwargs['post_id']
            if request.user != self.get_object().author:
                return redirect('posts:post_detail', post_id=post_id)
        return super().dispatch(request, *args, **kwargs)


@login_required
def add_comment(request, post_id):
    """Добавление комментариев."""
    post = get_object_or_404(Post, pk=post_id)
    form = CommentForm(data=request.POST or None)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()
    return redirect('posts:post_detail', post_id=post_id)


@login_required
def follow_index(request):
    """Посты, на которые подписан пользователь."""
    followed_posts = Post.objects.filter(
        author__following__user=request.user
    )
    posts = query_posts(followed_posts)
    page_obj = get_page_obj(request.GET.get('page'), list(posts))

    context = {
        'page_obj': page_obj,
    }
    return render(request, 'posts/follow.html', context)


@login_required
def profile_follow(request, username):
    """Подписаться на автора."""
    user = request.user
    author = get_object_or_404(User, username=username)
    with contextlib.suppress(IntegrityError):
        with transaction.atomic():
            Follow.objects.create(author=author, user=user)
    return redirect('posts:profile', username=username)


@login_required
def profile_unfollow(request, username):
    """Дизлайк, отписка."""
    user = request.user
    author = get_object_or_404(User, username=username)
    Follow.objects.filter(user=user, author=author).delete()
    return redirect('posts:profile', username=username)


@login_required
def rate_post(request, post_id):
    """Изменить рейтинг поста."""
    user = request.user
    post = get_object_or_404(Post, pk=post_id)

    # Автор не может ставить рейтинг своему посту
    if user == post.author:
        return redirect('posts:post_detail', post_id=post_id)

    form = RatingForm(data=request.POST or None)
    if form.is_valid():
        if rating := form.cleaned_data['rating']:
            Rating.objects.update_or_create(
                user=user, post=post,
                defaults={'rating': rating},
            )
    return redirect('posts:post_detail', post_id=post_id)
