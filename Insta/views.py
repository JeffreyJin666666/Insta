from django.shortcuts import render
from django.views.generic import TemplateView, ListView, DetailView
from Insta.models import Post, Like, InstaUser, UserConnection, Comment
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.urls import reverse, reverse_lazy
from annoying.decorators import ajax_request

# from django.contrib.auth.forms import UserCreationForm

from Insta.forms import CustomUserCreationForm
from django.contrib.auth.mixins import LoginRequiredMixin

# Create your views here.
class HelloWorld (TemplateView): #Helloworld这个view是继承自templateview的
    template_name = 'test.html'

class PostsView (LoginRequiredMixin, ListView):
    model = Post
    template_name = 'index.html'
    login_url = 'login'

    def get_queryset(self):
        current_user = self.request.user
        following = set()
        for conn in UserConnection.objects.filter(creator=current_user).select_related('following'):
            following.add(conn.following)
        return Post.objects.filter(author__in=following)  # 语法见 https://docs.djangoproject.com/en/3.0/ref/models/querysets/#id4

class PostDetailView (DetailView):
    model = Post
    template_name = 'post_detail.html'

class PostCreateView (LoginRequiredMixin, CreateView):
    model = Post
    template_name = 'post_create.html'
    fields = '__all__'  #不包含autofield，即migrate中的id field
    login_url = 'login'

class PostUpdateView (UpdateView):
    model = Post
    template_name = 'post_update.html'
    fields = '__all__'

class PostDeleteView (DeleteView):
    model = Post
    template_name = 'post_delete.html'
    success_url = reverse_lazy("posts")

class SignUp (CreateView):
    form_class = CustomUserCreationForm
    template_name = 'signup.html'
    success_url = reverse_lazy("login")

class UserDetailView (DetailView):
    model = InstaUser
    template_name = 'user_detail.html'

class UserUpdateView (UpdateView):
    model = InstaUser
    template_name = 'user_update.html'
    fields = ['username', 'password', 'email', 'profile_pic']
    success_url = reverse_lazy("posts")

@ajax_request
def addLike(request):
    post_pk = request.POST.get('post_pk')
    post = Post.objects.get(pk=post_pk)
    try:
        like = Like(post=post, user=request.user)
        like.save()
        result = 1
    except Exception as e:
        like = Like.objects.get(post=post, user=request.user)
        like.delete()
        result = 0

    return {
        'result': result,
        'post_pk': post_pk
    }

@ajax_request
def followUnfollow(request):
    follow_pk = request.POST.get('follow_user_pk')
    follow = InstaUser.objects.get(id=follow_pk)
    user_pk = request.POST.get('user_pk')
    curr_user = InstaUser.objects.get(id=user_pk)

    try:
        conn = UserConnection(creator=curr_user, following=follow)
        conn.save()
        result = 1
    except Exception as e:
        conn = UserConnection.objects.get(creator=curr_user, following=follow)
        conn.delete()
        result = 0

    return {
        'result': result,
    }

@ajax_request
def addComment(request):
    comment_text = request.POST.get('comment_text')
    post_pk = request.POST.get('post_pk')
    post = Post.objects.get(pk=post_pk)
    comm = Comment(user=request.user, post=post, comment=comment_text)
    comm.save()
    return {
        'result': 1,
        'post_pk': post_pk
    }