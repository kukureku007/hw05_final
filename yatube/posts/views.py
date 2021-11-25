from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.shortcuts import (get_object_or_404, redirect,
                              render)
from django.urls import reverse
from django.views.decorators.cache import cache_page

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


def paginator(request, posts):
    pag = Paginator(posts, POSTS_TO_SHOW)
    page_number = request.GET.get('page')
    page_obj = pag.get_page(page_number)
    return page_obj


@cache_page(20)
def index(request):
    posts = Post.objects.all()
    page_obj = paginator(request, posts)

    context = {
        'page_obj': page_obj,
    }
    return render(request, TEMPLATES['index'], context)


def group_posts(request, slug):
    group = get_object_or_404(Group, slug=slug)
    posts = group.posts.all()
    page_obj = paginator(request, posts)

    context = {
        'group': group,
        'page_obj': page_obj,
    }
    return render(request, TEMPLATES['group_list'], context)


def profile(request, username):
    author = get_object_or_404(User, username=username)
    page_obj = paginator(request, author.posts.all())

    following = True if (
        request.user.is_authenticated
        and author.following.filter(user=request.user).exists()) else False

    context = {
        'page_obj': page_obj,
        'author': author,
        'following': following
    }
    return render(request, TEMPLATES['profile'], context)


def post_detail(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    context = {
        'post': post,
        'form': CommentForm(
            request.POST or None
        )
    }
    return render(request, TEMPLATES['post_detail'], context)


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
    user = request.user
    authors = user.follower.all().values('author')

    posts = Post.objects.filter(author__in=authors)

    page_obj = paginator(request, posts)

    context = {
        'page_obj': page_obj,
    }
    return render(request, TEMPLATES['follow'], context)


@login_required
def profile_follow(request, username):
    follow = Follow(
        author=get_object_or_404(User, username=username),
        user=request.user
    )
    if follow.is_model_valid():
        follow.save()

    return redirect('posts:profile', username)


@login_required
def profile_unfollow(request, username):
    author = get_object_or_404(User, username=username)

    Follow.objects.filter(
        user=request.user,
        author=author
    ).delete()

    return redirect('posts:profile', username)
