from django.http import HttpResponse
from django.shortcuts import render, redirect
from .models import Product, Category, Profile
from django.contrib.auth import authenticate,login,logout
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django import forms
from .forms import SignUpForm,UpdateUserForm,ChangePasswordForm,UserInfoForm
from payment.forms import ShippingForm
from payment.models import ShippingAddress
from django.contrib import messages
from django import forms
import json
from cart.cart import Cart




def search(request):
    if request.method == 'POST':
        searched=request.POST['searched']
        searched=Product.objects.filter(name__icontains=searched)

        if not searched:
            messages.success(request, 'Nothing found')
            return render(request, 'core/search.html', {})
        else:
         return render(request, 'core/search.html', {'searched':searched})

    else:
        return render(request, 'core/search.html', {})


def update_info(request):
    if request.user.is_authenticated:
        current_user=Profile.objects.get(user__id=request.user.id)
        shipping_user=ShippingAddress.objects.get(user__id=request.user.id)
        form=UserInfoForm(request.POST or None, instance=current_user)
        shipping_form=ShippingForm(request.POST or None, instance=shipping_user)
        if form.is_valid() or shipping_form.is_valid():
            form.save()
            shipping_form.save()


            messages.success(request, 'Your account info  has been updated!')
            return redirect('core:index')

        return render(request,'core/update_info.html',{"form":form,"shipping_form":shipping_form})
    else:
        messages.info(request, 'Log in !')
        return redirect('core:login')

def update_password(request):
    if request.user.is_authenticated:
        current_user=request.user
        if request.method == 'POST':
             form=ChangePasswordForm(current_user,request.POST)
             if form.is_valid():
                 form.save()
                 login(request, current_user)
                 messages.success(request, 'Your password has been updated!')

                 return redirect('core:index')
             else:
                 for error in list(form.errors.values()):
                     messages.error(request, error)
                     return redirect('core:update_password')


        else:
         form=ChangePasswordForm(current_user)
         return render(request, 'core/update_password.html', {'form':form})
    else:
        messages.success(request, 'Log in ')
        return redirect('core:index')


def update_user(request):
    if request.user.is_authenticated:
        current_user=User.objects.get(id=request.user.id)
        user_form= UpdateUserForm(request.POST or None, instance=current_user)
        if user_form.is_valid():
            user_form.save()

            login(request, current_user)
            messages.success(request, 'Your account has been updated!')
            return redirect('core:index')

        return render(request,'core/update_user.html',{"user_form":user_form})
    else:
        messages.info(request, 'Log in !')
        return redirect('core:login')


def category_summary(request):
    categories = Category.objects.all()

    return render(request,'core/category_summary.html',{"categories":categories})


def category(request, name):
    cat = Category.objects.get(name=name)
    products = Product.objects.filter(category=cat)
    return render(request,'core/category.html',{'cat':cat,'products':products})

def product(request,name ):
    product = Product.objects.get(name=name)
    return render(request,'core/product.html',{'product':product})

def index(request):
    categories = Category.objects.all()
    products = Product.objects.all()
    return render(request,'core/index.html',{'products':products,'category':categories})

def about(request):
    return render(request,'core/about.html')
def login_user(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)

            current_user=Profile.objects.get(user__id=request.user.id)
            saved_cart=current_user.old_cart
            if saved_cart:
                converted_cart=json.loads(saved_cart)
                cart=Cart(request)
                for key,value in converted_cart.items():
                    cart.db_add(product=key, quantity=value)



            return redirect('core:index')
        else:
            return redirect('core:login')
    else:
        return render(request,'core/login.html')



def logout_user(request):
    logout(request)
    return redirect ('core:index')

def register_user(request):

    form = SignUpForm(request.POST)
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=password)
            login(request, user)
            return redirect('core:index')
        else:
            return redirect('core:register')
    else:
     return render(request,'core/register.html',{'form':form})