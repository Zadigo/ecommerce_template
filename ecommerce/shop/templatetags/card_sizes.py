from django import template

register = template.Library()

@register.filter
def size_in_row(index):
    sizes = [3, 5, 3]
    try:
        return sizes[index]
    except:
        pass