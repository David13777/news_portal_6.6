from celery import shared_task
import datetime
from django.conf import settings
from django.template.loader import render_to_string
from .models import Category, Post
from django.core.mail import EmailMultiAlternatives


@shared_task
def weekly_mail():
    today = datetime.datetime.now()
    last_week = today - datetime.timedelta(days=7)
    posts = Post.objects.filter(time_in__gte=last_week)
    categories = set(posts.values_list('category__name', flat=True))
    subscribers = set(Category.objects.filter(name__in=categories).values_list('subscribers__email', flat=True))
    html_content = render_to_string(
        'daily_post.html',
        {
            'link': settings.SITE_URL,
            'posts': posts,
        }
    )

    msg = EmailMultiAlternatives(
        subject='Weekly post',
        body='',
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=subscribers,
    )
    msg.attach_alternative(html_content, 'text/html')
    msg.send()


@shared_task
def email_send(pk):
    post = Post.objects.get(pk=pk)
    categories = post.categories.all()
    title = post.title()
    subscribers_emails = []
    for category in categories:
        subscribers_users = category.subscribers.all()
        for subscriber_user in subscribers_users:
            subscribers_emails.append(subscriber_user.email)
    html_content = render_to_string(
        'post.created_email.html',
        {
            'text': post.preview(),
            'link': f'{settings.SITE_URL}/news/{pk}'
        }
    )

    msg = EmailMultiAlternatives(
        subject=title,
        body='',
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=subscribers_emails,
    )
    msg.attach_alternative(html_content, 'text/html')
    msg.send()
