from django.db.models import Model
from django.shortcuts import render, redirect

from cart.cart import Cart
from payment.forms import ShippingForm,PaymentForms
from payment.models import ShippingAddress,Order,OrderItem
from django.contrib.auth.models import  User
from core.models import Product, Profile
import datetime
from django.shortcuts import get_object_or_404
from django.urls import reverse
from paypal.standard.forms import PayPalPaymentsForm
from django.conf import settings
import uuid


def orders(request, pk):
    if request.user.is_authenticated and request.user.is_superuser:

        order = get_object_or_404(Order, id=pk)

        items = OrderItem.objects.filter(order=order)
        if request.POST:
            status = request.POST['shipping_status']
            if status == "true":
                order = Order.objects.filter(id=pk)
                now= datetime.datetime.now()
                order.update(shipped=True,date_shipped=now)
                return redirect('core:index')

            else:
                 order = Order.objects.filter(id=pk)
                 order.update(shipped=False)
                 return redirect('core:index')
        return render(request, 'payment/orders.html', {
            "order": order,
            "items": items,

        })

    return redirect('core:index')


def not_shipped_dash(request):
    if request.user.is_authenticated and request.user.is_superuser:
        order = (
            Order.objects
            .filter(shipped=False)
            .prefetch_related('orderitem_set__product')
        )

        return render(
            request,
            "payment/not_shipped_dash.html",
            {"order": order}
        )

    return redirect('core:index')

def shipped_dash(request):

    if request.user.is_authenticated and request.user.is_superuser:
        order = (
            Order.objects
            .filter(shipped=True)
            .prefetch_related('orderitem_set__product')
        )

        return render(
            request,
            "payment/shipped_dash.html",
            {"order": order}
        )

    return redirect('core:index')


def process_order(request):
    if request.POST:
        cart = Cart(request)
        cart_products = cart.get_prods()
        quantity = cart.get_quants()
        totals = cart.cart_total()
        payment_form=PaymentForms(request.POST or None)
        my_shipping=request.session.get('my_shipping')
        full_name=my_shipping['shipping_full_name']
        email=my_shipping['shipping_email']
        amount_paid=totals
        shipping_address=f"{my_shipping['shipping_adress1']}\n{my_shipping['shipping_address2']}\n{my_shipping['shipping_city']}\n{my_shipping['shipping_state']}\n{my_shipping['shipping_zipcode']}\n{my_shipping['shipping_country']}\n"
        if request.user.is_authenticated:
            user = request.user
            create_order=Order(user=user,full_name=full_name,email=email,amount_paid=amount_paid,shipping_address=shipping_address)
            create_order.save()
            order_id=create_order.pk
            for product in cart_products:
                product_id=product.id
                if product.is_Sale:
                    price=product.sale_price
                else:
                    price=product.price

                for key,value in quantity.items():
                    if int(key)==product.id:
                        create_order_item=OrderItem(order_id=order_id,product_id=product_id,quantity=value,price=price,user=user)
                        create_order_item.save()
            for key in list(request.session.keys()):
                if key=="session_key":
                    del request.session[key]
            current_user=Profile.objects.filter(user__id=request.user.id)
            current_user.update(old_cart="")

            return redirect('core:index')

        else:

            create_order=Order(full_name=full_name,email=email,amount_paid=amount_paid,shipping_address=shipping_address)
            create_order.save()
            order_id = create_order.pk
            for product in cart_products:
                product_id = product.id
                if product.is_Sale:
                    price = product.sale_price
                else:
                    price = product.price

                for key, value in quantity.items():
                    if int(key) == product.id:
                        create_order_item = OrderItem(order_id=order_id, product_id=product_id, quantity=value,
                                                      price=price)
                        create_order_item.save()
            for key in list(request.session.keys()):
                if key=="session_key":
                    del request.session[key]
            return redirect('core:index')

    else:
        return redirect('core:index')


def billing_info(request):

    if request.POST:

        cart = Cart(request)
        cart_products = cart.get_prods()
        quantity = cart.get_quants()
        totals = cart.cart_total()
        my_shipping=request.POST
        request.session['my_shipping']=my_shipping

        host=request.get_host()
        paypal_dict={
            'business':settings.PAYPAL_RECEIVER_EMAIL,
            'amount':totals,
            'item_name':'Book Order',
            'no_shipping':'2',
            'invoice': str(uuid.uuid4()),
            'currency_code': 'EUR',
            'notify_url':'https://{}{}'.format(host,reverse("paypal-ipn")),
            'return_url': 'https://{}{}'.format(host, reverse("payment_success")),
            'cancel_return': 'https://{}{}'.format(host, reverse("payment_failed")),

        }
        paypal_form=PayPalPaymentsForm(initial=paypal_dict)
        if request.user.is_authenticated:
            billing_form=PaymentForms()
            return render(request, "payment/billing_info.html",
                          {"cart_products": cart_products, "quantity": quantity, "totals": totals,
                           "shipping_form": request.POST,"billing_form":billing_form,"paypal_form":paypal_form})

        else:
            billing_form = PaymentForms()

            return render(request, "payment/billing_info.html",
                          {"cart_products": cart_products, "quantity": quantity, "totals": totals,
                           "shipping_form": request.POST,"billing_form":billing_form,"paypal_form":paypal_form})


    else:
        return redirect('core:index')

def payment_success(request):

    return render(request,'payment/payment_success.html',{})
def payment_failed(request):

    return render(request,'payment/payment_failed.html',{})


def check_out(request):
    cart = Cart(request)
    cart_products = cart.get_prods
    quantity = cart.get_quants()
    totals = cart.cart_total()

    if request.user.is_authenticated:
        shipping_user=ShippingAddress.objects.get(user__id=request.user.id)
        shipping_form=ShippingForm(request.POST or None, instance=shipping_user)

        return render(request, "payment/check_out.html",
                      {"cart_products": cart_products, "quantity": quantity, "totals": totals, "shipping_form": shipping_form})
    else:
        shipping_form=ShippingForm(request.POST or None,)

        return render(request, "payment/check_out.html",
                      {"cart_products": cart_products, "quantity": quantity, "totals": totals,"shipping_form": shipping_form})



