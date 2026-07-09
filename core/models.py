from django.db import models
import datetime
from django.contrib.auth.models import User
from django.db.models.signals import post_save


class Profile(models.Model):
    user=models.OneToOneField(User,on_delete=models.CASCADE)
    date_modified=models.DateTimeField(User,auto_now=True)
    phone=models.CharField(max_length=100,default="",blank=True)
    address1=models.CharField(max_length=500,default="",blank=True)
    address2=models.CharField(max_length=500,default="",blank=True)
    city=models.CharField(max_length=100,default="",blank=True)
    zipcode=models.CharField(max_length=100,default="",blank=True)
    country=models.CharField(max_length=100,default="",blank=True)
    old_cart=models.CharField(max_length=100,default="",blank=True,null=True)
    def __str__(self):
        return self.user.username
def create_profile(sender,instance,created,**kwargs):
     if created:
        user_profile=Profile(user=instance)
        user_profile.save()


post_save.connect(create_profile,sender=User)

class Category(models.Model):
  name = models.CharField(max_length=100)
  def __str__(self):
      return self.name
class Customer(models.Model):
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    phone_number = models.CharField(max_length=10)
    email = models.EmailField()
    password=models.CharField(max_length=100)
    def __str__(self):
        return f'{self.first_name} {self.last_name}'
class Product(models.Model):
    name = models.CharField(max_length=100)
    price = models.DecimalField(default=0, max_digits=10, decimal_places=2)
    description = models.TextField(max_length=500,default="",blank=True,null=True)
    image=models.ImageField(upload_to='uploads/product/')
    category = models.ForeignKey(Category, on_delete=models.CASCADE,default=1)
    is_Sale=models.BooleanField(default=False)
    sale_price = models.DecimalField(default=0, max_digits=10, decimal_places=2)
    def __str__(self):
        return self.name
class Order(models.Model):
    product=models.ForeignKey(Product,on_delete=models.CASCADE,default=1)
    customer=models.ForeignKey(Customer,on_delete=models.CASCADE,default=1)
    quantity = models.IntegerField(default=1)
    address = models.CharField(max_length=500,default="",blank=True,null=True)
    phone=models.CharField(max_length=100,default="",blank=True,null=True)
    date=models.DateField(default=datetime.date.today)
    status=models.BooleanField(default=True)

    def __str__(self):
        return self.product