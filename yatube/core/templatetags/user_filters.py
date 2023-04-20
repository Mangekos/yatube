from django import template

"""Добавляем нащ фильтр шаблонов."""
register = template.Library()


@register.filter
def addclass(field, css):
    return field.as_widget(attrs={'class': css})
