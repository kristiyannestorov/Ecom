from .models import Category
from cart.cart import Cart

def categories(request):
    return {'category': Category.objects.all()}

def cart(request):
    return {'cart':Cart(request)}