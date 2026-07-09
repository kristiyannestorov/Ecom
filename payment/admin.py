from itertools import product

from django.contrib import admin
from .models import ShippingAddress,Order,OrderItem
from django.contrib.auth.models import User


admin.site.register(ShippingAddress)
admin.site.register(Order)
admin.site.register(OrderItem)


class OrderItemInline(admin.StackedInline):
    model=OrderItem
    extra=0


class  OrderAdmin(admin.ModelAdmin):
    model=Order
    readonly_fields=["date_ordered"]
    #dolnoto e ako iskash samo tezi neshta ako iskash neshto drugo trqbva da se dopishe
    #fields=["user","full_name","date_ordered"]
    inlines=[OrderItemInline]

admin.site.unregister(Order)
admin.site.register(Order,OrderAdmin)


