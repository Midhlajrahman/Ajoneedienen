from django import template
from main.models import CartItem

register = template.Library()


@register.simple_tag
def get_qty(session_key, option, restaurant):
    if CartItem.objects.filter(session_key=session_key, product=option, restaurant=restaurant).exists():
        item = CartItem.objects.filter(session_key=session_key, product=option, restaurant=restaurant).first()
        return item.quantity
    else:
        return 0
