from urllib.parse import urlencode

from django import template
from django.utils.encoding import force_str
from django.utils.safestring import mark_safe

register = template.Library()


def construct_query_string(context, query_params):
    # пустые значения будут удалены
    query_string = context['request'].path
    if len(query_params):
        encoded_params = urlencode([
            (key, force_str(value)) for (key, value) in query_params if value
        ]).replace('&', '&amp;')
        query_string += f'?{encoded_params}'
    return mark_safe(query_string)


def distrib_params(params, params_to_change):
    params_to_remove = []
    for item in params:
        if isinstance(item, dict):
            params_to_change.update(item)
        elif isinstance(item, tuple):
            params_to_change.update(dict((item,)))
        else:
            params_to_remove.append(item)
    return params_to_remove


@register.simple_tag(takes_context=True)
def modify_query(context, *params, **params_to_change):
    """Генерирует ссылку с модифицированными GET-параметрами."""
    params_to_remove = distrib_params(params, params_to_change)
    query_params = []
    for key, value_list in context['request'].GET.lists():
        if key not in params_to_remove:
            # игнорируем пару ключ-значения для 'params_to_remove'
            if key in params_to_change:
                # обновляем значения для ключей в 'params_to_change'
                query_params.append((key, params_to_change[key]))
                params_to_change.pop(key)
            else:
                # сохраняем остальные параметры, как есть
                query_params.extend((key, value) for value in value_list)
    # прикрепляем новые параметры
    query_params.extend(
        (key, value) for key, value in params_to_change.items()
    )
    return construct_query_string(context, query_params)
