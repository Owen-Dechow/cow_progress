from django.template.defaulttags import register


@register.filter
def dic(dictionary, key):
    return dictionary.get(key)
