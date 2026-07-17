from django.shortcuts import render, redirect
from cart.cart import Cart
from payment.forms import ShippingForm, PaymentForms
from payment.models import ShippingAddress, Order, OrderItem
from django.contrib.auth.models import User
from django.contrib import messages
from core.models import Product, Profile
import datetime

from django.urls import reverse
from paypal.standard.forms import PayPalPaymentsForm
from django.conf import settings
import uuid


def orders(request, pk):
    if request.user.is_authenticated and request.user.is_superuser:
        # Get the order
        order = Order.objects.get(id=pk)
        # Get the order items
        items = OrderItem.objects.filter(order=pk)

        if request.POST:
            status = request.POST['shipping_status']
            # Check if true or false
            if status == "true":
                # Get the order
                order = Order.objects.filter(id=pk)
                # Update the status
                now = datetime.datetime.now()
                order.update(shipped=True, date_shipped=now)
            else:
                # Get the order
                order = Order.objects.filter(id=pk)
                # Update the status
                order.update(shipped=False)
            messages.success(request, "Shipping Status Updated")
            return redirect('home')

        return render(request, 'payment/orders.html', {"order": order, "items": items})

    else:
        messages.success(request, "Access Denied")
        return redirect('home')


def not_shipped_dash(request):
    if request.user.is_authenticated and request.user.is_superuser:
        orders = Order.objects.filter(shipped=False)
        if request.POST:
            status = request.POST['shipping_status']
            num = request.POST['num']
            # Get the order
            order = Order.objects.filter(id=num)
            # grab Date and time
            now = datetime.datetime.now()
            # update order
            order.update(shipped=True, date_shipped=now)
            # redirect
            messages.success(request, "Shipping Status Updated")
            return redirect('home')

        return render(request, "payment/not_shipped_dash.html", {"orders": orders})
    else:
        messages.success(request, "Access Denied")
        return redirect('home')


def shipped_dash(request):
    if request.user.is_authenticated and request.user.is_superuser:
        orders = Order.objects.filter(shipped=True)
        if request.POST:
            status = request.POST['shipping_status']
            num = request.POST['num']
            # grab the order
            order = Order.objects.filter(id=num)
            # grab Date and time
            now = datetime.datetime.now()
            # update order
            order.update(shipped=False)
            # redirect
            messages.success(request, "Shipping Status Updated")
            return redirect('home')

        return render(request, "payment/shipped_dash.html", {"orders": orders})
    else:
        messages.success(request, "Access Denied")
        return redirect('home')


def _create_order_from_session(request):
    """
    Shared helper: builds an Order + OrderItems from the cart and the
    shipping/invoice info stashed in the session during billing_info().
    Returns the created Order, or None if the required session data is
    missing (e.g. this view was hit directly without going through
    billing_info first).
    """
    cart = Cart(request)
    cart_products = cart.get_prods()
    quantity = cart.get_quants()
    totals = cart.cart_total()

    my_shipping = request.session.get('my_shipping')
    my_invoice = request.session.get('my_invoice')

    if not my_shipping or not my_invoice:
        return None

    # Avoid creating a duplicate order if this view is somehow hit twice
    # (e.g. user refreshes the success page) for the same invoice.
    existing = Order.objects.filter(invoice=my_invoice).first()
    if existing:
        return existing

    full_name = my_shipping['shipping_full_name']
    email = my_shipping['shipping_email']
    amount_paid = totals
    shipping_address = (
        f"{my_shipping['shipping_adress1']}\n"
        f"{my_shipping['shipping_address2']}\n"
        f"{my_shipping['shipping_city']}\n"
        f"{my_shipping['shipping_state']}\n"
        f"{my_shipping['shipping_zipcode']}\n"
        f"{my_shipping['shipping_country']}\n"
    )

    user = request.user if request.user.is_authenticated else None

    create_order = Order(
        user=user,
        full_name=full_name,
        email=email,
        amount_paid=amount_paid,
        shipping_address=shipping_address,
        invoice=my_invoice,
    )
    create_order.save()
    order_id = create_order.pk

    for product in cart_products:
        product_id = product.id
        price = product.sale_price if product.is_Sale else product.price

        for key, value in quantity.items():
            if int(key) == product.id:
                OrderItem.objects.create(
                    order_id=order_id,
                    product_id=product_id,
                    quantity=value,
                    price=price,
                    user=user,
                )

    if request.user.is_authenticated:
        Profile.objects.filter(user__id=request.user.id).update(old_cart="")

    for key in ("my_shipping", "my_invoice", "session_key"):
        if key in request.session:
            del request.session[key]

    return create_order


def process_order(request):
    # Kept for any flow that still POSTs here directly (e.g. a "pay on
    # delivery" button that skips PayPal). Uses the same helper as
    # payment_success so order creation logic lives in one place.
    if request.POST:
        create_order = _create_order_from_session(request)
        if create_order is None:
            messages.success(request, "Nothing to process")
        return redirect('core:index')
    else:
        return redirect('core:index')


def billing_info(request):
    if request.POST:
        # Get the cart
        cart = Cart(request)
        cart_products = cart.get_prods
        quantities = cart.get_quants
        totals = cart.cart_total()

        # Create a session with Shipping Info
        my_shipping = request.POST
        request.session['my_shipping'] = my_shipping

        # Get the host
        host = request.get_host()

        # Generate invoice and store it in session so it can be retrieved
        # once PayPal redirects back to payment_success()
        invoice_id = str(uuid.uuid4())
        request.session['my_invoice'] = invoice_id

        # Create Paypal Form Dictionary
        paypal_dict = {
            'business': settings.PAYPAL_RECEIVER_EMAIL,
            'amount': totals,
            'item_name': 'Book Order',
            'no_shipping': '2',
            'invoice': invoice_id,
            'currency_code': 'USD',  # EUR for Euros
            'notify_url': 'https://{}{}'.format(host, reverse("paypal-ipn")),
            'return_url': 'https://{}{}'.format(host, reverse("payment_success")),
            'cancel_return': 'https://{}{}'.format(host, reverse("payment_failed")),
        }

        # Create actual paypal button
        paypal_form = PayPalPaymentsForm(initial=paypal_dict)

        # Get The Billing Form (same for both branches, so build it once)
        billing_form = PaymentForms()

        return render(request, "payment/billing_info.html",
                      {"paypal_form": paypal_form, "cart_products": cart_products, "quantities": quantities,
                       "totals": totals, "shipping_info": request.POST, "billing_form": billing_form})

    else:
        messages.success(request, "Access Denied")
        return redirect('home')


def check_out(request):
    # Get the cart
    cart = Cart(request)
    cart_products = cart.get_prods
    quantities = cart.get_quants
    totals = cart.cart_total()

    if request.user.is_authenticated:
        # Checkout as logged in user
        # Shipping User
        shipping_user = ShippingAddress.objects.get(user__id=request.user.id)
        # Shipping Form
        shipping_form = ShippingForm(request.POST or None, instance=shipping_user)
        return render(request, "payment/check_out.html",
                      {"cart_products": cart_products, "quantities": quantities, "totals": totals,
                       "shipping_form": shipping_form})
    else:
        # Checkout as guest
        shipping_form = ShippingForm(request.POST or None)
        return render(request, "payment/check_out.html",
                      {"cart_products": cart_products, "quantities": quantities, "totals": totals,
                       "shipping_form": shipping_form})


def payment_success(request):
    # PayPal redirects here (GET) after a successful sandbox payment.
    # Create the order now, using the shipping/invoice info saved in the
    # session back in billing_info().
    _create_order_from_session(request)
    for key in ("my_shipping", "my_invoice", "session_key"):
        if key in request.session:
            del request.session[key]

    return render(request, "payment/payment_success.html", {})


def payment_failed(request):
    return render(request, "payment/payment_failed.html", {})