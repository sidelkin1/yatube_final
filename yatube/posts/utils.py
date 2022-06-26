from django.conf import settings
from django.core.paginator import Paginator
from django.db import models
from django.db.models import FloatField
from django.db.models.functions import Round

from .forms import SORTING_CHOICES

FloatField.register_lookup(Round)


def get_page_obj(page_number, posts):
    """Возвращает объект-пагинатор для постов."""
    paginator = Paginator(posts, settings.POSTS_PER_PAGE)
    return paginator.get_page(page_number)


def create_facets(form):
    """Формируем заготовку для фильтров."""
    facets = {
        'selected': {'sorting': SORTING_CHOICES[0]},
        'categories': {}
    }
    for name, field in form.fields.items():
        if name in ['rating', 'sorting']:
            facets['categories'] |= {name: field.choices}
        else:
            facets['categories'] |= {name: tuple(
                (items[0].value, items[1]) for items in field.choices
            )}
    return facets


def filter_facets(facets, posts, form):
    """Фильтрует посты в соответствии с формой."""
    for param, choices in facets['categories'].items():
        if value := form.cleaned_data[param]:
            if param == 'rating':
                selected_value = int(value)
                posts = (
                    posts.filter(rating_avg__round=selected_value).distinct()
                )
            elif param == 'sorting':
                selected_value = value
                posts = posts.order_by(value)
            else:
                selected_value = value.pk
                posts = posts.filter(**{param: value}).distinct()
            facets['selected'][param] = (
                selected_value,
                dict(choices)[selected_value]
            )
    return posts


def query_posts(queryset):
    """Выборка постов со статистикой по кол-ву и рейтингу."""
    subqueries = (
        ('author_count', models.Count, 'author__posts'),
        ('group_count', models.Count, 'group__posts'),
        ('rating_avg', models.Avg, 'ratings__rating'),
        ('rating_count', models.Count, 'ratings'),
        ('comment_count', models.Count, 'comments'),
    )
    for agg_field, agg_fun, group in subqueries:
        subquery = models.Subquery(
            queryset
            .filter(pk=models.OuterRef('pk'))
            .annotate(**{agg_field: agg_fun(group)})
            .values(agg_field)
        )
        queryset = queryset.annotate(**{agg_field: subquery})
    return queryset.select_related('author', 'group')
