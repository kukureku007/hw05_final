from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.core.cache import cache
from django.core.paginator import Paginator
from django.db.utils import IntegrityError
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
# from django.views.decorators.cache import cache_page

from .forms import CommentForm, PostForm
from .models import Follow, Group, Post

POSTS_TO_SHOW = settings.POSTS_TO_SHOW
User = get_user_model()

TEMPLATES = {
    'index': 'posts/index.html',
    'group_list': 'posts/group_list.html',
    'profile': 'posts/profile.html',
    'post_detail': 'posts/post_detail.html',
    'create_post': 'posts/create_post.html',
    'follow': 'posts/follow.html'
}

CACHE_KEYS = {
    'index': 'index-cache',
    'follow': 'follows-{user}',
    'group_posts': '{slug}-posts',
}


def paginator(request, posts):
    pag = Paginator(posts, POSTS_TO_SHOW)
    page_number = request.GET.get('page')
    page_obj = pag.get_page(page_number)
    return page_obj


def index(request):
    """
    Вывод постов на главной странице.
    Добавлены: пагинация, кэш.
    """
    posts = cache.get(CACHE_KEYS['index'])
    if not posts:
        posts = Post.objects.all().select_related(
            'author',
            'group'
        )
        cache.set(CACHE_KEYS['index'], posts)

    page_obj = paginator(request, posts)

    context = {
        'page_obj': page_obj,
    }
    return render(request, TEMPLATES['index'], context)


def group_posts(request, slug):
    """
    Вывод постов одной группы.
    Добавлены: пагинация, кэш.
    """
    group_posts = cache.get(CACHE_KEYS['group_posts'].format(slug=slug))
    if not group_posts:
        group_posts = get_object_or_404(
            Group,
            slug=slug
        ).posts.all().prefetch_related('author')
        cache.set(CACHE_KEYS['group_posts'].format(slug=slug), group_posts)

    group = None
    if group_posts.count() > 1:
        group = group_posts[0].group.slug
    else:
        group = get_object_or_404(Group, slug=slug)

    page_obj = paginator(
        request,
        group_posts,
    )

    context = {
        'group': group,
        'page_obj': page_obj,
    }
    return render(request, TEMPLATES['group_list'], context)


# cache author posts counts and
def profile(request, username):
    author = get_object_or_404(User, username=username)
    page_obj = paginator(
        request,
        author.posts.all().prefetch_related('group')
    )

    following = True if (
        request.user.is_authenticated
        and author.following.filter(user=request.user).exists()
    ) else False

    context = {
        'page_obj': page_obj,
        'author': author,
        'following': following
    }
    return render(request, TEMPLATES['profile'], context)


# cache post, comments
def post_detail(request, post_id):
    post = get_object_or_404(
        Post.objects.select_related(
            'author',
            'group',
        ),
        pk=post_id
    )
    is_edit_allowed = True if (
        request.user == post.author
    ) else False
    context = {
        'post': post,
        'form': CommentForm(
            request.POST or None
        ),
        'is_edit_allowed': is_edit_allowed,
    }
    return render(request, TEMPLATES['post_detail'], context)


# clear cache of group author
@login_required
def post_create(request):
    form = PostForm(
        request.POST or None,
        files=request.FILES or None
    )
    if request.method == 'POST':
        if form.is_valid():
            post = form.save(commit=False)
            author = request.user
            post.author = author
            post.save()
            return redirect(reverse('posts:profile', args=(author.username,)))

    context = {
        'form': form
    }
    return render(request, TEMPLATES['create_post'], context)


# clear cache of group if required
@login_required
def post_edit(request, post_id):
    post = get_object_or_404(Post, pk=post_id)

    if request.user != post.author:
        return redirect(reverse('posts:post_detail', args=(post_id,)))

    form = PostForm(
        request.POST or None,
        files=request.FILES or None,
        instance=post
    )
    if request.method == 'POST':
        if form.is_valid():
            form.save()
            return redirect(reverse('posts:post_detail', args=(post_id,)))

    context = {
        'form': form,
        'is_edit': True,
    }
    return render(request, TEMPLATES['create_post'], context)


# clear cache comment post
@login_required
def add_comment(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    form = CommentForm(request.POST or None)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()
    return redirect('posts:post_detail', post_id=post_id)


@login_required
def follow_index(request):
    """
    Вывод постов всех авторов, на которых подписан текущий пользователь.
    Добавлены: пагинация, кэш.
    """
    posts = cache.get(CACHE_KEYS['follow'].format(user=request.user))
    if not posts:
        posts = Post.objects.filter(
            author__following__user=request.user
        ).select_related('author', 'group',)
        cache.set(CACHE_KEYS['follow'].format(user=request.user), posts)

    page_obj = paginator(request, posts)

    context = {
        'page_obj': page_obj,
    }
    return render(request, TEMPLATES['follow'], context)


@login_required
def profile_follow(request, username):
    """
    Подписка на автора.
    Добавлены: кэш.
    """
    try:
        Follow.objects.create(
            author=get_object_or_404(User, username=username),
            user=request.user,
        )
        cache.delete(CACHE_KEYS['follow'].format(user=request.user))
    except IntegrityError as e:
        raise Http404(e.__cause__)
    return redirect('posts:profile', username)


@login_required
def profile_unfollow(request, username):
    """
    Отписка от автора.
    Добавлены: кэш.
    """
    get_object_or_404(
        Follow,
        user=request.user,
        author=User.objects.get(username=username)
    ).delete()
    cache.delete(CACHE_KEYS['follow'].format(user=request.user))
    return redirect('posts:profile', username)
