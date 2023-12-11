import datetime
import json

from cart.models import *
from cart.views import _cart_id
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.cache import never_cache
from user_profile.models import *

from .forms import FormWithCaptcha
from .models import *
from .forms import *


# Create your views here.
@never_cache
@login_required(login_url="userauth:login")
def checkout(request, total=0, quantity=0, cart_items=None):
    try:
        address = Address.objects.filter(user=request.user)
        profile = User_profile.objects.get(user=request.user)
    except:
        address = None
        profile = None
        messages.warning(request, 'Please complete your profile to proceed.')
        return redirect('user_profile:profile')

    cart_item = Cartitem.objects.filter(user=request.user)
    all_cart_item = not any(item.product.stock <= 0 for item in cart_item)

    if not all_cart_item:
        messages.error(request, 'One of the selected items is out of stock.')
        return redirect("cart:cart")

    try:
        tax = 0
        grand_total = 0
        shipping = 0

        cart_items = Cartitem.objects.filter(user=request.user, is_active=True)

        if not cart_items.exists():
            return redirect("main:shop")

        for cart_item in cart_items:
            product_price = cart_item.product.price
            product_offer = cart_item.product.offer
            category_offer = cart_item.product.category.offer
            
            if product_offer is None and category_offer is None:
                total += product_price * cart_item.quantity
                quantity += cart_item.quantity
            else:
                if product_offer and category_offer:
                    discount = max(product_offer.discount, category_offer.discount)
                elif product_offer:
                    discount = product_offer.discount
                else:
                    discount = category_offer.discount
                
                discount_price = (discount / 100) * float(product_price)
                discount_amount = float(product_price) - discount_price
                total += discount_amount * cart_item.quantity
                quantity += cart_item.quantity

        tax = (2 * total) / 100
        shipping = 20
        grand_total = total + shipping + tax

    except ObjectDoesNotExist:
        pass

    context = {
        "total": total,
        "quantity": quantity,
        "cart_items": cart_items,
        "captcha": FormWithCaptcha,
        "tax": tax,
        "shipping": shipping,
        "grandtotal": grand_total,
        "address": address,
        "profile": profile,
    }

    return render(request, "order/checkout.html", context)


@never_cache
@login_required(login_url="userauth:login")
def place_order(request, total=0, quantity=0):
    try:
        current_user = request.user
        cart_items = Cartitem.objects.filter(user=current_user)
        cart_count = cart_items.count()

        if request.method == "POST":
            selected_address_id = request.POST.get("address")
            payment_method = request.POST.get("pay-method")
            captcha = request.POST.get("g-recaptcha-response")

            if not selected_address_id:
                messages.error(request,"Please add an address from your profile to proceed")
                return redirect("orders:checkout")

            if not captcha:
                messages.error(request, "Confirm you are not a Robot")
                return redirect("orders:checkout")

            if payment_method == "COD":
                selected_address = get_object_or_404(
                    Address, id=selected_address_id, user=current_user
                )
                profile = User_profile.objects.get(user=current_user)

                tax = 0
                grand_total = 0
                shipping = 20  # Fixed shipping cost

                for cart_item in cart_items:
                    product_price = cart_item.product.price
                    product_offer = cart_item.product.offer
                    category_offer = cart_item.product.category.offer
                    
                    if product_offer is  None and category_offer is None:
                        total += cart_item.product.price * cart_item.quantity
                        quantity += cart_item.quantity
                    else:
                        if product_offer and category_offer:
                            discount = max(product_offer.discount,category_offer.discount)
                        elif product_offer:
                            discount = product_offer.discount
                        else:
                            discount = category_offer.discount
                        discount_price = (discount / 100) * float(product_price)
                        discount_amount = float(product_price) - discount_price
                        total += discount_amount * cart_item.quantity
                        quantity += cart_item.quantity

                tax = (2 * total) / 100
                grand_total = total + shipping + tax

                if 'disc_total' in request.session:
                    grand_total = request.session['disc_total']
                    del request.session['disc_total']

                data = Order(
                    user=current_user,
                    payment=payment_method,
                    first_name=profile.first_name,
                    last_name=profile.last_name,
                    phone=profile.mobile_number,
                    phone2=selected_address.phone,
                    email=profile.user.email,
                    address_line_1=selected_address.address,
                    state=profile.state,
                    district=selected_address.district,
                    zipcode=selected_address.zipcode,
                    hometown=selected_address.hometown,
                    order_total=grand_total,
                    tax=tax,
                    ip=request.META.get("REMOTE_ADDR"),
                    is_ordered=True,
                )

                data.save()

                if payment_method == "COD":
                    data.payment_status = "Pending"

                yr = int(datetime.date.today().strftime("%Y"))
                dt = int(datetime.date.today().strftime("%d"))
                mt = int(datetime.date.today().strftime("%m"))
                d = datetime.date(yr, mt, dt)
                current_date = d.strftime("%Y%m%d")
                order_number = current_date + str(data.id)
                data.order_number = order_number
                data.save()

                cart_items = Cartitem.objects.filter(user=request.user)
                for item in cart_items:
                    orderproduct = OrderProduct(
                        order=data,
                        payment=payment_method,
                        user=request.user,
                        product=item.product,
                        quantity=item.quantity,
                        product_price=item.product.price,
                        ordered=True,
                    )

                    orderproduct.save()

                    product = item.product
                    product.stock -= item.quantity
                    product.save()

                Cartitem.objects.filter(user=request.user).delete()

                if cart_count <= 0:
                    print(cart_count)
                    return redirect("main:shop")

                return render(request, "order/thankyou.html")
            
            elif payment_method == 'wallet':
                wallet = Wallet.objects.get(user=current_user)
                selected_address = get_object_or_404(
                    Address, id=selected_address_id, user=current_user
                )
                profile = User_profile.objects.get(user=current_user)

                tax = 0
                grand_total = 0
                shipping = 20  # Fixed shipping cost

                for cart_item in cart_items:
                    product_price = cart_item.product.price
                    product_offer = cart_item.product.offer
                    category_offer = cart_item.product.category.offer
                    
                    if product_offer is  None and category_offer is None:
                        total += cart_item.product.price * cart_item.quantity
                        quantity += cart_item.quantity
                    else:
                        if product_offer and category_offer:
                            discount = max(product_offer.discount,category_offer.discount)
                        elif product_offer:
                            discount = product_offer.discount
                        else:
                            discount = category_offer.discount
                        discount_price = (discount / 100) * float(product_price)
                        discount_amount = float(product_price) - discount_price
                        total += discount_amount * cart_item.quantity
                        quantity += cart_item.quantity


                tax = (2 * total) / 100
                grand_total = total + shipping + tax

                if 'disc_total' in request.session:
                    grand_total = request.session['disc_total']
                    del request.session['disc_total']

                if wallet.wallet < grand_total:
                    messages.error(request, "Insufficient funds in the wallet.")
                    return redirect("orders:checkout")
                
                wallet.wallet -= grand_total
                wallet.save()

                transaction_record = Transaction.objects.create(
                    user=current_user,
                    wallet=wallet,
                    amount=grand_total,
                    note="Payment for order",
                    transaction="Dr",
                )
                transaction_record.save()
                data = Order(
                    user=current_user,
                    payment=payment_method,
                    payment_status = "Completed",
                    first_name=profile.first_name,
                    last_name=profile.last_name,
                    phone=profile.mobile_number,
                    phone2=selected_address.phone,
                    email=profile.user.email,
                    address_line_1=selected_address.address,
                    state=profile.state,
                    district=selected_address.district,
                    zipcode=selected_address.zipcode,
                    hometown=selected_address.hometown,
                    order_total=grand_total,
                    tax=tax,
                    ip=request.META.get("REMOTE_ADDR"),
                    is_ordered=True,
                )

                data.save()


                yr = int(datetime.date.today().strftime("%Y"))
                dt = int(datetime.date.today().strftime("%d"))
                mt = int(datetime.date.today().strftime("%m"))
                d = datetime.date(yr, mt, dt)
                current_date = d.strftime("%Y%m%d")
                order_number = current_date + str(data.id)
                data.order_number = order_number
                data.save()

                cart_items = Cartitem.objects.filter(user=request.user)
                for item in cart_items:
                    orderproduct = OrderProduct(
                        order=data,
                        payment=payment_method,
                        user=request.user,
                        product=item.product,
                        quantity=item.quantity,
                        product_price=item.product.price,
                        ordered=True,
                    )

                    orderproduct.save()

                    product = item.product
                    product.stock -= item.quantity
                    product.save()

                Cartitem.objects.filter(user=request.user).delete()

                if cart_count <= 0:
                    print(cart_count)
                    return redirect("main:shop")

                return render(request, "order/thankyou.html")

            else:
                selected_address = get_object_or_404(
                    Address, id=selected_address_id, user=current_user
                )
                profile = User_profile.objects.get(user=current_user)

                tax = 0
                grand_total = 0
                shipping = 20  # Fixed shipping cost

                for cart_item in cart_items:
                    product_price = cart_item.product.price
                    product_offer = cart_item.product.offer
                    category_offer = cart_item.product.category.offer
                    
                    if product_offer is  None and category_offer is None:
                        total += cart_item.product.price * cart_item.quantity
                        quantity += cart_item.quantity
                    else:
                        if product_offer and category_offer:
                            discount = max(product_offer.discount,category_offer.discount)
                        elif product_offer:
                            discount = product_offer.discount
                        else:
                            discount = category_offer.discount
                        discount_price = (discount / 100) * float(product_price)
                        discount_amount = float(product_price) - discount_price
                        total += discount_amount * cart_item.quantity
                        quantity += cart_item.quantity

                tax = (2 * total) / 100
                grand_total = total + shipping + tax

                if 'disc_total' in request.session:
                    grand_total = request.session['disc_total']
                    del request.session['disc_total']


                data = Order(
                    user=current_user,
                    payment=payment_method,
                    first_name=profile.first_name,
                    last_name=profile.last_name,
                    phone=profile.mobile_number,
                    phone2=selected_address.phone,
                    email=profile.user.email,
                    address_line_1=selected_address.address,
                    state=profile.state,
                    district=selected_address.district,
                    zipcode=selected_address.zipcode,
                    hometown=selected_address.hometown,
                    order_total=grand_total,
                    tax=tax,
                    ip=request.META.get("REMOTE_ADDR"),
                )

                data.save()

                yr = int(datetime.date.today().strftime("%Y"))
                dt = int(datetime.date.today().strftime("%d"))
                mt = int(datetime.date.today().strftime("%m"))
                d = datetime.date(yr, mt, dt)
                current_date = d.strftime("%Y%m%d")
                order_number = current_date + str(data.id)
                data.order_number = order_number
                data.save()

                pending_order = Order.objects.get(
                    user=current_user, is_ordered=False, order_number=order_number
                )

                context = {
                    "order": pending_order,
                    "cart_items": cart_items,
                    "total": total,
                    "tax": tax,
                    "grand_total": grand_total,
                }
                return render(request, "order/onlinepayment.html", context)

        return render(request, "order/thankyou.html")
    except Exception as e:
        messages.error(request,"Complete your user profile to make an order")
        return redirect('user_profile:profile')

@login_required(login_url='userauth:login')
def apply_coupon(request, total=0, quantity=0):
    if request.method == "POST":
        code = request.POST.get("coupon-code")

    if not code.strip():
        messages.error(request, "No coupon code found")
        return redirect("coupon")

    try:
        coupon = Coupons.objects.get(code=code, is_active=True)
    except Coupons.DoesNotExist:
        messages.error(request, "Invalid coupon code")
        return redirect("orders:checkout")

    try:
        # Check if the user has already used the coupon
        coupon_usage = CouponUsage.objects.get(
            user=request.user, coupon=coupon, used=False
        )
    except CouponUsage.DoesNotExist:
        messages.error(request, "Coupon not available for use")
        return redirect("orders:checkout")

    # Rest of your existing code remains unchanged
    address = Address.objects.filter(user=request.user)
    profile = User_profile.objects.get(user=request.user)

    try:
        tax = 0
        grand_total = 0
        shipping = 0

        cart_items = Cartitem.objects.filter(user=request.user, is_active=True)

        if not cart_items.exists():
            return redirect("main:shop")

        for cart_item in cart_items:
            total += cart_item.product.price * cart_item.quantity
            quantity += cart_item.quantity

        tax = (2 * total) / 100
        shipping = 20
        grand_total = total + shipping + tax

        discount = (grand_total * coupon.discount) / 100
        grand_total -= discount

        request.session['disc_total']= float(grand_total)

        # Update CouponUsage with order-specific information
        coupon_usage.total_amount = grand_total
        coupon_usage.discount_amount = discount
        coupon_usage.used = True

        
        coupon_usage.save()

    except ObjectDoesNotExist:
        pass

    context = {
        "total": total,
        "quantity": quantity,
        "cart_items": cart_items,
        "captcha": FormWithCaptcha,
        "tax": tax,
        "discount": discount,
        "shipping": shipping,
        "grandtotal": grand_total,
        "address": address,
        "profile": profile,
    }

    return render(request, "order/checkout.html", context)

@login_required(login_url='userauth:login')
def online_payment(request):
    body = json.loads(request.body)
    order = Order.objects.get(
        user=request.user, is_ordered=False, order_number=body["orderID"]
    )

    cart_items = Cartitem.objects.filter(user=request.user)
    cart_count = cart_items.count()

    payment = onlinePayment(
        user=request.user,
        order=order,
        payment_id=body["transID"],
        payment_method=body["payment_method"],
        amount_paid=order.order_total,
        status=body["status"],
    )

    payment.save()
    order.payment = payment.payment_method
    order.is_ordered = True
    order.payment_status = "Completed"
    order.save()

    cart_items = Cartitem.objects.filter(user=request.user)
    for item in cart_items:
        orderproduct = OrderProduct(
            order=order,
            payment=payment.payment_method,
            user=request.user,
            product=item.product,
            quantity=item.quantity,
            product_price=item.product.price,
            ordered=True,
        )

        orderproduct.save()

        product = item.product
        product.stock -= item.quantity
        product.save()

    Cartitem.objects.filter(user=request.user).delete()
    if cart_count <= 0:
        print(cart_count)
        return redirect("main:shop")

    data = {
        "order_number": order.order_number,
        "transID": payment.payment_id,
    }

    return JsonResponse(data)

@login_required(login_url='userauth:login')
def order_sucsses(request):
    return render(request, "order/thankyou.html")


def list_order(request):
    orders = Order.objects.filter(soft_delete=False,is_ordered=True).order_by('-created_at')
    order_status_choices = Order.STATUS
    context = {"orders": orders, "order_status_choices": order_status_choices}
    return render(request, "order/list_orders.html", context)


def change_status(request, id):
    order = Order.objects.get(id=id, is_ordered=True)

    if request.method == "POST":
        payment_status = request.POST.get("payment-status")
        order_status = request.POST.get("order-status")

        print(payment_status, order_status)
        order.status = order_status
        order.payment_status = payment_status
        order.save()

        if order.payment_status == "Completed":
            applicable_coupon = (
                Coupons.objects.filter(
                    is_active=True, min_amount__lte=order.order_total
                )
                .order_by("-min_amount")
                .first()
            )

            if applicable_coupon:
                if not CouponUsage.objects.filter(
                    user=request.user, coupon=applicable_coupon
                ):
                    coupon_usage = CouponUsage(
                        user=request.user,
                        coupon=applicable_coupon,
                        code=applicable_coupon.code,
                        used=False,
                    )

                    coupon_usage.save()

        return redirect("orders:list_orders")

    return redirect("orders:list_orders")


def view_order(request, id):
    order = Order.objects.get(id=id, is_ordered=True)
    product = OrderProduct.objects.filter(order=order)

    context = {
        "order": order,
        "product": product,
    }

    return render(request, "order/vieworders.html", context)


def soft_remove(request, id):
    order = Order.objects.get(id=id)
    order.soft_delete = True
    order.save()
    return redirect("orders:list_orders")


def order_delete(request, id):
    order = Order.objects.get(id=id)
    order.delete()
    return redirect("orders:list_orders")


def submit_review(request, id):
    url = request.META.get('HTTP_REFERER')

    if request.method == 'POST':
        try:
            reviews = ReviewRating.objects.get(user__id=request.user.id, product__id=id)
            form = ReviewForm(request.POST, instance=reviews)
            form.save()
            messages.success(request, 'Thank you, your review has been Updated')
            return redirect(url)
        except ReviewRating.DoesNotExist:
            form = ReviewForm(request.POST)
            if form.is_valid():
                data = ReviewRating()
                data.rating = form.cleaned_data['rating']
                data.review = form.cleaned_data['review']
                
                profile = User_profile.objects.get(user=request.user)

                data.ip = request.META.get('REMOTE_ADDR')
                data.product_id = id
                data.user_id = request.user.id
                data.profile = profile
                data.save()
                messages.success(request, 'Thank you, your review has been Submitted')
                return redirect(url)

