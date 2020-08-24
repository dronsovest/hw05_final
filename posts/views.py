from django.core.paginator import Paginator
from django.shortcuts import render, get_object_or_404, redirect,\
    get_list_or_404
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model

from .models import Post, Group, Comment, Follow
from .forms import PostForm, CommentForm


User = get_user_model()


def index(request):
    post_list = Post.objects.all()
    paginator = Paginator(post_list, 10)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    return render(request, 'index.html', {
                                            'page': page,
                                            'paginator': paginator,
                                         })


def group_posts(request, slug):
    group = get_object_or_404(Group, slug=slug)
    posts = group.posts.all()
    paginator = Paginator(posts, 5)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    return render(request, 'group.html', {
                                            'group': group,
                                            'page': page,
                                            'paginator': paginator
                                         })


@login_required
def new_post(request):
    form = PostForm()
    header_name = "Добавить запись"
    button_name = "Добавить"
    if not request.method == "POST":
        return render(request, "new.html", {
                                                "form": form,
                                                "header_name": header_name,
                                                "button_name": button_name
                                            })
    form = PostForm(request.POST, files=request.FILES)
    if not form.is_valid():
        return render(request, "new.html", {
                                                "form": form,
                                                "header_name": header_name,
                                                "button_name": button_name
                                            })
    post_get = form.save(commit=False)
    post_get.author = request.user
    post_get.save()
    return redirect("/")


def profile(request, username):
    author = get_object_or_404(User, username=username)
    posts = author.posts.all()
    paginator = Paginator(posts, 5)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    following = False
    if Follow.objects.filter(user=request.user, author=author).count() > 0:
        following = True
    return render(request, 'profile.html', {
                                                'posts': posts,
                                                'author': author,
                                                'page': page,
                                                'paginator': paginator,
                                                'following': following,
                                            })


def post_view(request, username, post_id):
    post = get_object_or_404(Post, pk=post_id)
    author = get_object_or_404(User, username=username)
    comments = post.comments.all()
    posts_count = author.posts.all().count()
    form = CommentForm
    return render(request, 'post.html', {
                                            'post': post,
                                            'posts': posts_count,
                                            'author': author,
                                            'form': form,
                                            'items': comments,
                                        })


def post_edit(request, username, post_id):
    post = get_object_or_404(Post, id=post_id)
    if post.author != request.user:
        return redirect("post", username=post.author, post_id=post_id)
    form = PostForm(
        request.POST or None,
        files=request.FILES or None,
        instance=post)
    header_name = "Редактировать запись"
    button_name = "Сохранить"
    if not form.is_valid():
        return render(request, "new.html", {
                                                "form": form,
                                                "header_name": header_name,
                                                "button_name": button_name,
                                                "post": post,
                                            })
    post_get = form.save(commit=False)
    post_get.author = request.user
    post_get.pk = post_id
    post_get.pub_date = post.pub_date
    post_get.save()
    return redirect("post", username=post.author, post_id=post_id)


def page_not_found(request, exception):
    return render(
        request, 
        "misc/404.html", 
        {"path": request.path}, 
        status=404
    )


def server_error(request):
    return render(request, "misc/500.html", status=500)


@login_required
def add_comment(request, username, post_id):
    post = get_object_or_404(Post, id=post_id)
    form = CommentForm()
    if not request.method == "POST":
        return render(request, "comments.html", {
                                                    "form": form,
                                                    "post": post,
                                                })
    form = CommentForm(request.POST or None)
    if not form.is_valid():
        return render(request, "comments.html", {
                                                    "form": form,
                                                    "post": post,
                                                })
    comment_get = form.save(commit=False)
    comment_get.author = request.user
    comment_get.post = post
    comment_get.save()
    return redirect("post", username=username, post_id=post_id)


@login_required
def follow_index(request):
    post_list = Post.objects.filter(author__following__user=request.user)
    paginator = Paginator(post_list, 10)
    page_number = request.GET.get("page")
    page = paginator.get_page(page_number)
    return render(request, "follow.html", {
                                            "page": page,
                                            "paginator": paginator,
                                          })


@login_required
def profile_follow(request, username):
    author = get_object_or_404(User, username=username)
    if request.user == author: 
        return redirect("profile", username=username)
    new_follow = Follow(user=request.user, author=author)
    new_follow.save()
    return redirect("profile", username=username)


@login_required
def profile_unfollow(request, username):
    author = get_object_or_404(User, username=username)
    Follow.objects.filter(user=request.user, author=author).delete()
    return redirect ("profile", username=username)
