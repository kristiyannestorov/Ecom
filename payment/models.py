from django.db import models
from django.contrib .auth.models import User
from core.models import Product
from django.db.models.signals import post_save,pre_save
from django.dispatch import receiver
import datetime

class ShippingAddress(models.Model):
    user=models.ForeignKey(User,on_delete=models.CASCADE,null=True,blank=True)
    shipping_full_name=models.CharField(max_length=100,default='')
    shipping_email=models.EmailField(max_length=100,default='')
    shipping_adress1=models.CharField(max_length=100,default='')
    shipping_address2=models.CharField(max_length=100,default='')
    shipping_state=models.CharField(max_length=100,default='')
    shipping_zipcode=models.CharField(max_length=100,default='')
    shipping_country=models.CharField(max_length=100,default='')
    shipping_city=models.CharField(max_length=100,default='')


    class Meta:
        verbose_name_plural = "Shipping Address"

    def __str__(self):
        return f'Shipping Address-{str(self.id)}'

def create_shipping(sender,instance,created, **kwargs):

    if created:
      user_shipping=ShippingAddress(user=instance)
      user_shipping.save()
post_save.connect(create_shipping,sender=User)

class Order(models.Model):
    user=models.ForeignKey(User,on_delete=models.CASCADE,null=True,blank=True)
    full_name=models.CharField(max_length=100)
    email=models.EmailField(max_length=100)
    shipping_address=models.TextField(max_length=100)
    amount_paid=models.DecimalField(max_digits=10,decimal_places=2)
    date_ordered = models.DateTimeField(auto_now_add=True)
    shipped=models.BooleanField(default=False)
    date_shipped=models.DateTimeField(blank=True, null=True)
    invoice=models.CharField(max_length=100,null=True,blank=True)
    paid=models.BooleanField(default=False)
    def __str__(self):
        return f'Order {str(self.id)}'
@receiver(pre_save,sender=Order)
def set_shipped_date_on_update(sender,instance,**kwargs):
    if instance.pk:
        now=datetime.datetime.now()
        obj=sender._default_manager.get(pk=instance.pk)
        if instance.shipped and not obj.shipped:
            instance.date_shipped=now


class OrderItem(models.Model):
    order=models.ForeignKey(Order,on_delete=models.CASCADE,null=True)
    product=models.ForeignKey(Product,on_delete=models.CASCADE,null=True)
    user=models.ForeignKey(User,on_delete=models.CASCADE,null=True,blank=True)
    quantity=models.PositiveBigIntegerField(default=1)
    price=models.DecimalField(max_digits=10,decimal_places=2)
    def __str__(self):
        return f'Order Item {str(self.id)}'



