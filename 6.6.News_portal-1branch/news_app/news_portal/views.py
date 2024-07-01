from datetime import datetime

from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, get_object_or_404, render
from django.template.loader import render_to_string
from django.views.generic import ListView, DetailView, CreateView, DeleteView, UpdateView
from .models import Post, Category, User
from .filters import PostFilter
from .forms import PostForm
from django.urls import reverse_lazy, resolve
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.core.mail import send_mail, EmailMultiAlternatives
from django.core.cache import cache


class PostList(ListView):
    model = Post
    ordering = '-time_in'
    template_name = 'news.html'
    context_object_name = 'news'
    paginate_by = 10

    def get_queryset(self):
        queryset = super().get_queryset()
        self.filterset = PostFilter(self.request.GET, queryset)
        return self.filterset.qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['time_in'] = datetime.utcnow()
        return context


class PostDetail(DetailView):
    model = Post
    template_name = 'news_one.html'
    context_object_name = 'news_one'
    pk_url_kwarg = 'pk'

    def get_object(self, *args, **kwargs):  # переопределяем метод получения объекта, как ни странно
        obj = cache.get(f'news_one-{self.kwargs["pk"]}',
                        None)  # кэш очень похож на словарь, и метод get действует так же. Он забирает значение по ключу, если его нет, то забирает None.

        # если объекта нет в кэше, то получаем его и записываем в кэш
        if not obj:
            obj = super().get_object(queryset=self.queryset)
            cache.set(f'news_one-{self.kwargs["pk"]}', obj)
            return obj


class SearchList(ListView):
    model = Post
    filterset_class = PostFilter
    template_name = 'search.html'
    context_object_name = 'search'
    paginate_by = 10

    def get_queryset(self):
        queryset = super().get_queryset()
        self.filterset = PostFilter(self.request.GET, queryset)
        return self.filterset.qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['filterset'] = self.filterset
        return context


class PostCreate(CreateView, LoginRequiredMixin, PermissionRequiredMixin):
    permission_required = ('news_portal.add_post',)
    form_class = PostForm
    model = Post
    template_name = 'post_create.html'
    context_object_name = 'post_create'

    def form_valid(self, form):
        post = form.save(commit=False)
        if self.request.path == '/news/article/create/':
            post.type = 'A'
        post.save()
        return super().form_valid(form)


class PostUpdate(UpdateView, LoginRequiredMixin, PermissionRequiredMixin):
    permission_required = ('news_portal.change_post',)
    form_class = PostForm
    model = Post
    template_name = 'post_edit.html'
    context_object_name = 'post_edit'

    def get_object(self, **kwargs):
        id = self.kwargs.get('pk')
        return Post.objects.get(pk=id)


class PostDelete(DeleteView, LoginRequiredMixin, PermissionRequiredMixin):
    permission_required = ('news_portal.delete_post',)
    model = Post
    template_name = 'post_delete.html'
    context_object_name = 'post_delete'
    success_url = reverse_lazy('news')



@login_required
def subscribe(request, pk):
    user = request.user
    category = Category.objects.get(id=pk)
    category.subscribers.add(user)
    message = 'You have successfully subscribed to the category:'
    return render(request, 'subscribe.html', {'category': category, 'message': message})


class PostCategory(ListView):
    model = Post
    template_name = 'category.html'
    context_object_name = 'category_news'

    def get_queryset(self):
        self.category = get_object_or_404(Category, id=self.kwargs['pk'])
        queryset = Post.objects.filter(category=self.category).order_by('-time_in')
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['is_not_subscriber'] = self.request.user not in self.category.subscribers.all()
        context['category'] = self.category
        return context



