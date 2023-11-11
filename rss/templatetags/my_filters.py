from django import template

register = template.Library()


@register.filter()
def upfirstletter(value, arg):
    d = ''
    for i in value:
        if i.isupper():
           d = d + " " + i
        else:
            d = d+i
    return d
