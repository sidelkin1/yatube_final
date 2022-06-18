import math

from django import template
from posts.models import RATING_CHOICES

# Для регистрации нашего фильтра
register = template.Library()


@register.filter
def addclass(field, css):
    """Добавляем обязательный класс для полей формы."""
    return field.as_widget(attrs={'class': css})


@register.filter
def todict(param, pk):
    """Для передачи именованных параметров в modify_query."""
    return {param: pk}


@register.filter
def totuple(param, pk):
    """Для передачи именованных параметров в modify_query."""
    return (param, pk)


@register.filter
def getitem(d, key):
    """Для извлечения нужного значения из словаря."""
    return d.get(key)


@register.filter
def getstars(rating_avg):
    """Для расчета нужного кол-ва звездочек в рейтинге."""
    fraction, integer = (
        math.modf(rating_avg) if rating_avg else (0, 0)
    )
    full = int(integer)
    half = int(fraction >= 0.5)
    return {
        'full': full,
        'half': half,
        'empty': len(RATING_CHOICES) - full - half,
    }
