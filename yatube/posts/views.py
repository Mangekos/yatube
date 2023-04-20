from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from .models import Post, Group, User, Comment, Follow
from django.core.paginator import Paginator
from .forms import PostForm, CommentForm
from django.views.decorators.cache import cache_page


NUMBER_POSTS = 10


def get_paginator(posts, request):
    """Пагинатор"""
    paginator = Paginator(posts, NUMBER_POSTS)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return page_obj


@cache_page(20)
def index(request):
    """Главная страница"""
    posts = Post.objects.all()
    title = 'Последние обновления на сайте'
    context = {
        'title': title,
        'page_obj': get_paginator(posts, request),
    }
    return render(request, 'posts/index.html', context)


def group_posts(request, slug):
    """View-функция для страницы сообщества:"""
    group = get_object_or_404(Group, slug=slug)
    title = (f'Записи сообщества {group}')
    posts = group.posts.all()
    context = {
        'group': group,
        'title': title,
        'page_obj': get_paginator(posts, request),
    }
    return render(request, 'posts/group_list.html', context)


def profile(request, username):
    """Информация о профиле"""
    author = get_object_or_404(User, username=username)
    posts = author.posts.all()
    following = author.following.all()
    context = {
        'author': author,
        'page_obj': get_paginator(posts, request),
        'following': following,
    }
    return render(request, 'posts/profile.html', context)


def post_detail(request, post_id):
    """Информация о постах"""
    form = CommentForm(request.POST or None)
    post = get_object_or_404(Post, pk=post_id)
    comments = Comment.objects.filter(post=post)
    context = {
        'post': post,
        'comments': comments,
        'form': form,
    }
    return render(request, 'posts/post_detail.html', context)


@login_required
def post_create(request):
    """Создание поста"""
    form = PostForm(request.POST or None, files=request.FILES or None,)
    if form.is_valid():
        post = form.save(commit=False)
        post.author = request.user
        post.save()
        return redirect('posts:profile', username=request.user)
    context = {
        'form': form
    }
    return render(request, 'posts/create_post.html', context)


@login_required
def post_edit(request, post_id):
    """Редактирование поста"""
    post = get_object_or_404(Post, pk=post_id)
    is_edit = True
    form = PostForm(
        request.POST or None,
        files=request.FILES or None,
        instance=post
    )
    if request.user != post.author:
        return redirect('posts:post_detail', post_id=post.pk)
    if form.is_valid():
        post.save()
        return redirect('posts:post_detail', post_id=post.pk)
    context = {
        'form': form,
        'is_edit': is_edit,
    }
    return render(request, 'posts/create_post.html', context)


@login_required
def add_comment(request, post_id):
    """Добавить комментарий к посту"""
    post = get_object_or_404(Post, pk=post_id, )
    form = CommentForm(request.POST or None)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()
    return redirect('posts:post_detail', post_id=post_id)


@login_required
def follow_index(request):
    """Страница избранные авторы"""
    posts = Post.objects.filter(author__following__user=request.user)
    context = {
        'page_obj': get_paginator(posts, request),
    }
    return render(request, 'posts/follow.html', context)


@login_required
def profile_follow(request, username):
    """Подписка на автора"""
    author = get_object_or_404(User, username=username)
    if author != request.user:
        Follow.objects.get_or_create(
            user=request.user,
            author=author,
        )
    return redirect("posts:follow_index")


@login_required
def profile_unfollow(request, username):
    """Отписаться от автора"""
    author = get_object_or_404(User, username=username)
    Follow.objects.get(
        user=request.user,
        author=author,
    ).delete()
    return redirect("posts:follow_index")
