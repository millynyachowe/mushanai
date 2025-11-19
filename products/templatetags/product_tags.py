from django import template

register = template.Library()


@register.filter
def stars(value):
    """
    Convert a rating (0-5) to star display
    """
    if value is None:
        return ""
    try:
        rating = float(value)
        stars_html = ""
        for i in range(1, 6):
            if i <= rating:
                stars_html += "⭐"
            else:
                stars_html += "☆"
        return stars_html
    except (ValueError, TypeError):
        return ""


@register.filter
def int_rating(value):
    """
    Convert rating to integer for comparison
    """
    try:
        return int(float(value))
    except (ValueError, TypeError):
        return 0

