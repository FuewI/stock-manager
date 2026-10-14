from django import template

register = template.Library()


@register.filter
def row_letter(value):
    try:
        number = int(value)
    except (TypeError, ValueError):
        return ''

    if number < 1:
        return ''

    result = ''

    while number:
        number, remainder = divmod(number - 1, 26)
        result = chr(65 + remainder) + result

    return result