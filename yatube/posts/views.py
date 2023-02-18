from django.contrib.auth.decorators import login_required
from django.http import HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views.decorators.cache import cache_page

from core.utils import paginate
from posts.forms import CommentForm, PostForm
from posts.models import Follow, Group, Post, User


@cache_page(20, key_prefix='index_page')
def index(request: HttpRequest) -> HttpResponse:
    posts = Post.objects.select_related('author', 'group')
    return render(
        request,
        'posts/index.html',
        {
            'page_obj': paginate(
                request,
                posts,
            ),
        },
    )


def group_posts(request: HttpRequest, slug: str) -> HttpResponse:
    group = get_object_or_404(Group, slug=slug)
    posts = group.posts.all()
    return render(
        request,
        'posts/group_list.html',
        {
            'group': group,
            'page_obj': paginate(
                request,
                posts,
            ),
        },
    )


def profile(request: HttpRequest, username: str) -> HttpResponse:
    author = get_object_or_404(User, username=username)
    posts = author.posts.all()
    following = (
        request.user.is_authenticated
        and Follow.objects.filter(
            author=author,
            user=request.user,
        ).exists()
    )
    return render(
        request,
        'posts/profile.html',
        {
            'author': author,
            'following': following,
            'page_obj': paginate(
                request,
                posts,
            ),
        },
    )


@login_required
def post_create(request: HttpRequest) -> HttpResponse:
    form = PostForm(request.POST or None)
    if form.is_valid():
        form.instance.author = request.user
        form.save()
        return redirect(
            reverse(
                'posts:profile',
                args=(request.user.username,),
            ),
        )

    return render(request, 'posts/create_post.html', {'form': form})


@login_required
def post_edit(request: HttpRequest, pk: int) -> HttpResponse:
    post = get_object_or_404(Post, pk=pk)
    if post.author != request.user:
        return redirect('posts:post_detail', pk=pk)
    form = PostForm(
        data=request.POST or None,
        files=request.FILES or None,
        instance=post,
    )
    if form.is_valid():
        form.save()
        return redirect('posts:post_detail', pk=pk)
    return render(
        request,
        'posts/create_post.html',
        {'form': form, 'post': post, 'is_edit': True},
    )


def post_detail(request: HttpRequest, pk: int) -> HttpResponse:
    post = get_object_or_404(Post, pk=pk)
    form = CommentForm(request.POST or None)
    return render(
        request,
        'posts/post_detail.html',
        {
            'post': post,
            'form': form,
        },
    )


@login_required
def add_comment(request: HttpRequest, pk: int) -> HttpResponse:
    post = get_object_or_404(Post, pk=pk)
    form = CommentForm(request.POST or None)
    if form.is_valid():
        form.instance.author = request.user
        form.instance.post = post
        form.save()
    return redirect('posts:post_detail', pk=pk)


@login_required
def follow_index(request: HttpRequest) -> HttpResponse:
    posts = Post.objects.filter(author__following__user=request.user)
    return render(
        request,
        'posts/follow.html',
        {
            'page_obj': paginate(
                request,
                posts,
            ),
        },
    )


@login_required
def profile_follow(request: HttpRequest, username: str) -> HttpResponse:
    author = get_object_or_404(User, username=username)
    if request.user != author:
        Follow.objects.get_or_create(user=request.user, author=author)
    return redirect('posts:profile', username=username)


@login_required
def profile_unfollow(request: HttpRequest, username: str) -> HttpResponse:
    get_object_or_404(
        Follow,
        author__username=username,
        user=request.user,
    ).delete()
    return redirect('posts:profile', username=username)
