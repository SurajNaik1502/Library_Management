from django import template

register = template.Library()

@register.filter
def shelf_image(nearest_shelf, book_location):
    # Ensure the values are strings for concatenation
    return f'maps/_{"".join([str(nearest_shelf), str(book_location)])}.png'
