from django.urls import path
from .views import PostList, PostDetail, SearchList, PostCreate, PostDelete, PostUpdate, PostCategory, subscribe
from django.views.decorators.cache import cache_page


urlpatterns = [
   path('', cache_page(60)(PostList.as_view()), name='news'),
   path('<int:pk>/', cache_page(300)(PostDetail.as_view()), name='news_one'),
   path('search/', SearchList.as_view()),
   path('post_create/', PostCreate.as_view()),
   path('<int:pk>/post_edit/', PostUpdate.as_view()),
   path('<int:pk>/post_delete/', PostDelete.as_view()),
   path('article/post_create/', PostCreate.as_view()),
   path('article/<int:pk>/post_edit/', PostUpdate.as_view()),
   path('article/<int:pk>/post_delete/', PostDelete.as_view()),
   path('category/<int:pk>/', PostCategory.as_view(), name='category'),
   path('category/subscribe/<int:pk>/', subscribe, name='subscribe')

]

