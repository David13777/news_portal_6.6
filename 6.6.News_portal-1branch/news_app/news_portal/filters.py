from django_filters import FilterSet, DateFilter, ModelChoiceFilter
from .models import Post, Category, Author
from .forms import *


class PostFilter(FilterSet):
    date = DateFilter(field_name='time_in', lookup_expr='gt', widget=forms.DateInput(attrs={'type': 'date'}), label='Published on')
    title = ModelChoiceFilter(field_name='category', queryset=Category.objects.all(), label='Category')
    author = ModelChoiceFilter(field_name='author', queryset=Author.objects.all(), label='Author')

    class Meta:
        model = Post
        fields = {
            'title': ['icontains'],
            'author': ['exact'],
            'time_in': ['gt'],
        }



