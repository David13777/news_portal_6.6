from django.db import models
from django.contrib.auth.models import User
from django.db.models import Sum
from django.urls import reverse
from django.core.cache import cache


class Author(models.Model):
    author = models.OneToOneField(User, on_delete=models.CASCADE)
    author_rating = models.IntegerField(default=0)

    def __str__(self):
        return self.author.username

    def update_rating(self):
        all_post_rating = Post.objects.filter(author_id=self.pk).aggregate(post_rating=Sum('post_rating'))['post_rating'] * 3
        author_comment_rating = Comment.objects.filter(user_id=self.author).aggregate(comment_rating=Sum('comment_rating'))['comment_rating']
        post_comment_rating = Comment.objects.filter(post__author__author=self.author).aggregate(comment_rating=Sum('comment_rating'))['comment_rating']
        self.author_rating = all_post_rating + author_comment_rating + post_comment_rating
        self.save()
        return self.author_rating


class Category(models.Model):
    name_category = models.CharField(max_length=124, unique=True)
    subscribers = models.ManyToManyField(User, related_name='category')

    def get_subscribers(self):
        return self.subscribers

    def get_category(self):
        return self.name_category

    def __str__(self):
        return self.name_category


article = 'A'
news = 'N'
KIND = [
    (article, 'Article'),
    (news, 'News')
]


class Post(models.Model):
    author = models.ForeignKey(Author, on_delete=models.CASCADE)
    post_kind = models.CharField(max_length=1, choices=KIND, default=news)
    time_in = models.DateTimeField(auto_now_add=True)
    category = models.ManyToManyField(Category, through='PostCategory')
    title = models.CharField(max_length=255)
    content = models.TextField()
    post_rating = models.IntegerField(default=0)

    def like(self):
        self.post_rating += 1
        self.save()

    def dislike(self):
        self.post_rating -= 1
        self.save()

    def preview(self):
        return f'{self.content[0:124]}...'

    def __str__(self):
        return f'{self.title}:{self.content[:20]} ({self.time_in})'

    def get_absolute_url(self):
        return reverse('news_one', args=[str(self.id)])

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)  # сначала вызываем метод родителя, чтобы объект сохранился
        cache.delete(f'news_one-{self.pk}')  # затем удаляем его из кэша, чтобы сбросить его


class PostCategory(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)

    def __str__(self):
        return self.category


class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    comment_text = models.TextField()
    time_in = models.DateTimeField(auto_now_add=True)
    comment_rating = models.IntegerField(default=0)

    def like(self):
        self.comment_rating += 1
        self.save()

    def dislike(self):
        self.comment_rating -= 1
        self.save()

    def __str__(self):
        return self.comment_text


