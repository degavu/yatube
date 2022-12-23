from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import cache_page

from .models import Post, Group, Comment, User, Follow
from .forms import PostForm, CommentForm
from .utils import page_objects
from django.conf import settings as yatube_conf


@cache_page(yatube_conf.TIME_CACHE_SECONDS, key_prefix='index_page')
def index(request):
    post_list = Post.objects.select_related('author')
    page_obj = page_objects(request, post_list)
    context = {'page_obj': page_obj}
    template = 'posts/index.html'
    return render(request, template, context)


def group_posts(request, slug):
    group = get_object_or_404(Group, slug=slug)
    post_list = Post.objects.filter(group=group)
    page_obj = page_objects(request, post_list)
    context = {'page_obj': page_obj}
    template = 'posts/group_list.html'
    return render(request, template, context)


def profile(request, username):
    user = get_object_or_404(User, username=username)
    post_list = Post.objects.filter(author=user)
    page_obj = page_objects(request, post_list)
    if request.user.is_authenticated:
        following = Follow.objects.filter(
            user=request.user, author=user).exists()
    else:
        following = None
    context = {'page_obj': page_obj,
               'author': user,
               'following': following,
               }
    return render(request, 'posts/profile.html', context)


def post_detail(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    comments = Comment.objects.filter(post=post)
    context = {
        'post': post,
        'comments': comments,
        'form': CommentForm()
    }
    return render(request, 'posts/post_detail.html', context)


@login_required
def post_create(request):
    form = PostForm(request.POST or None, files=request.FILES or None)
    if form.is_valid():
        post = form.save(commit=False)
        post.author = request.user
        post.save()
        return redirect('posts:profile', request.user)
    return render(request, 'posts/create_post.html', {'form': form})


@login_required
def post_edit(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    if request.user != post.author:
        return redirect('posts:profile', post.author)
    form = PostForm(request.POST or None,
                    files=request.FILES or None,
                    instance=post)
    if form.is_valid():
        post = form.save(commit=False)
        post.id = post_id
        post.author = request.user
        post.save()
        return redirect('posts:post_detail', post_id)
    return render(
        request,
        'posts/create_post.html',
        {'form': form, 'is_edit': True}
    )


@login_required
def add_comment(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    form = CommentForm(request.POST or None)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()
    return redirect('posts:post_detail', post_id=post_id)


@login_required
def follow_index(request):
    all_posts = Post.objects.select_related('author')
    post_list = all_posts.filter(author__following__user=request.user)
    page_obj = page_objects(request, post_list)
    context = {
        'page_obj': page_obj,
    }
    template = 'posts/follow.html'
    return render(request, template, context)


@login_required
def profile_follow(request, username):
    follow_to = get_object_or_404(User, username=username)
    already_follower = Follow.objects.filter(
        user=request.user, author=follow_to)
    if not (already_follower.exists()):
        if (request.user != follow_to):
            Follow.objects.create(user=request.user, author=follow_to)
    return redirect('posts:profile', username=follow_to)


@login_required
def profile_unfollow(request, username):
    unfollow_to = get_object_or_404(User, username=username)
    Follow.objects.filter(
        user=request.user, author=unfollow_to).delete()
    return redirect('posts:follow_index')
