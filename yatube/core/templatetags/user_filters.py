from django import template
register = template.Library()


@register.filter
def addclass(field, css):
    return field.as_widget(attrs={'class': css})


@register.filter
def uglify(convert_text):
    i = 1
    new_text = ''
    for char in convert_text:
        if (i % 2) == 0:
            new_text = new_text + char.upper()
        else:
            new_text = new_text + char.lower()
        i = i + 1
    return new_text
