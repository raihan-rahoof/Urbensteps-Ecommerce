import re

from adminside.models import *
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.shortcuts import get_object_or_404, redirect, render
from orders.models import *

from .models import *

# Create your views here.


@login_required(login_url="userauth:login")
def profile(request):
    if request.user.is_authenticated:
        user = Custom_user.objects.get(id=request.user.id)
        try:
            profile = User_profile.objects.get(user=request.user)
        except User_profile.DoesNotExist:
            profile = None

        context = {"user": user, "profile": profile}
        return render(request, "profile/profile.html", context)
    else:
        return redirect("user_auth:login")


@login_required(login_url="userauth:login")
def update_profile(request):
    if User_profile.objects.filter(user=request.user):
        profile = get_object_or_404(User_profile, user=request.user)
    else:
        profile = User_profile.objects.create(user=request.user)

    if request.method == "POST":
        firstname = request.POST.get("firstname")
        lastname = request.POST.get("lastname")
        gender = request.POST.get("gender")
        state = request.POST.get("state")
        mobile = request.POST.get("mobile")
        pic = request.FILES.get("pic")

        phone_pattern = re.compile(
            r"^(\+91)?\s*?(\d{3})\s*?(-)?\s*?(\d{3})\s*?(-)?\s*?(\d{4})$"
        )
        if not phone_pattern.match(mobile):
            messages.error(
                request, "Invalid phone number format. Please use the format +91 ..."
            )
            return redirect("user_profile:address")

        if pic:
            profile.first_name = firstname
            profile.last_name = lastname
            profile.gender = gender
            profile.state = state
            profile.profile = pic

            # Convert mobile to an integer before saving
            if mobile is not None:
                profile.mobile_number = int(mobile)

            profile.save()
        else:
            profile.first_name = firstname
            profile.last_name = lastname
            profile.gender = gender
            profile.state = state

            # Convert mobile to an integer before saving
            if mobile is not None:
                profile.mobile_number = int(mobile)

            profile.save()

        return redirect("user_profile:profile")

    # Handle GET requests (if needed)
    return redirect("user_profile:edit_profile")


@login_required(login_url="userauth:login")
def address(request):
    # Get or create User_profile for the current user
    profile, created = User_profile.objects.get_or_create(user=request.user)

    user_address = Address.objects.filter(user=request.user)

    context = {
        "profile": profile,
        "user_address": user_address,
    }
    return render(request, "profile/address.html", context)


@login_required(login_url="userauth:login")
def add_address(request):
    count = request.session.get("address_count", 0)

    if count >= 3:
        messages.error(request, "Maximum 3 addresses allowed")
        return redirect("user_profile:address")
    else:
        if request.method == "POST":
            district = request.POST["district"]
            hometown = request.POST["hometown"]
            zipcode = request.POST["zipcode"]
            address = request.POST["address"]
            phone = request.POST["phone"]

            pin_pattern = re.compile(r"^\d{6}$")
            if not pin_pattern.match(zipcode):
                messages.error(request, "Invalid pin code")
                return redirect("user_profile:address")

            phone_pattern = re.compile(
                r"^(\+91)?\s*?(\d{3})\s*?(-)?\s*?(\d{3})\s*?(-)?\s*?(\d{4})$"
            )
            if not phone_pattern.match(phone):
                messages.error(
                    request,
                    "Invalid phone number format. Please use the format +91 ...",
                )
                return redirect("user_profile:address")

            user_address = Address.objects.create(
                user=request.user,
                district=district,
                hometown=hometown,
                zipcode=zipcode,
                address=address,
                phone=phone,
            )

            user_address.save()

            count += 1
            request.session["address_count"] = count

            messages.success(request, "Successfully added")
            return redirect("user_profile:address")

        return redirect("user_profile:address")


@login_required(login_url="userauth:login")
def delete_address(request, id):
    user_address = Address.objects.filter(id=id)
    user_address.delete()
    count = request.session.get("address_count", 0)
    count -= 1
    request.session["address_count"] = count
    messages.success(request, "Address deleted succsesfully")
    return redirect("user_profile:address")


@login_required(login_url="userauth:login")
def update_address(request, id):
    if request.method == "POST":
        district = request.POST["district"]
        hometown = request.POST["hometown"]
        zipcode = request.POST["zipcode"]
        address = request.POST["address"]
        phone = request.POST["phone"]

        pin_pattern = re.compile(r"^\d{6}$")
        if not pin_pattern.match(zipcode):
            messages.error(request, "Invalid pin code")
            return redirect("user_profile:address")

        phone_pattern = re.compile(
            r"^(\+91)?\s*?(\d{3})\s*?(-)?\s*?(\d{3})\s*?(-)?\s*?(\d{4})$"
        )
        if not phone_pattern.match(phone):
            messages.error(
                request, "Invalid phone number format. Please use the format +91 ..."
            )
            return redirect("user_profile:address")

        user_address = Address.objects.get(id=id)
        user_address.district = district
        user_address.hometown = hometown
        user_address.zipcode = zipcode
        user_address.address = address
        user_address.phone = phone

        user_address.save()
        messages.success(request, "Edited Succssesfully")
        return redirect("user_profile:address")
    return redirect("user_profile:address")


@login_required(login_url="userauth:login")
def order_track(request):
    try:
        profile = User_profile.objects.get(user=request.user)
        orders = Order.objects.filter(user=request.user, is_ordered=True).order_by(
            "-id"
        )
        orderproducts = OrderProduct.objects.filter(user=request.user)

    except Order.DoesNotExist:
        orders = None
        orderproducts = None
        profile = None

    context = {
        "profile": profile,
        "orders": orders,
        "orderproducts": orderproducts,
    }
    return render(request, "profile/orders.html", context)


@login_required(login_url="userauth:login")
def cancel_product(request, id, oid):
    if request.method == "POST":
        cancel_reason = request.POST.get("cancel_reason")

        if len(cancel_reason) < 15:
            messages.error(request, "Must be atleast 20 words")
            return redirect("user_profile:cancel_product")

        order = Order.objects.get(id=oid)
        ordered_product = OrderProduct.objects.get(id=id)
        reason = Cancelorder.objects.create(
            order_product=ordered_product, user=request.user, reason=cancel_reason
        )

        counter = OrderProduct.objects.filter(order=order).count()

        products = OrderProduct.objects.filter(order=order)

        ordered_product.status = "Cancelled"
        ordered_product.ordered = False
        ordered_product.product.stock += ordered_product.quantity

        ordered_product.save()
        ordered_product.product.save()

        count = 0

        order.order_total -= ordered_product.product_price

        for product in products:
            if product.status == "Cancelled":
                count += 1

        if count == counter:
            order.status = "Cancel"
            order.order_total = 0

        order.save()
        reason.save()

        return redirect("user_profile:order-track")

    return render(request, "profile/cancel_product.html")


@login_required(login_url="userauth:login")
def cancel_order(request, id):
    if request.method == "POST":
        cancel_reason = request.POST.get("cancel_reason")

        if len(cancel_reason) < 15:
            messages.error(request, "Must be atleast 20 words")
            return redirect("user_profile:cancel_order")

        order = Order.objects.get(id=id)

        orderproducts = OrderProduct.objects.filter(user=request.user)
        reason = Cancelorder.objects.create(
            order=order, user=request.user, reason=cancel_reason
        )
        reason.save()
        order.status = "Cancel"
        order.save()
        print(order.status)
        for product in orderproducts:
            product.status = "Cancelled"
            product.ordered = False
            product.product.stock += product.quantity
            product.save()
            product.product.save()

        return redirect("user_profile:order-track")

    return render(request, "profile/cancel_order.html")


@login_required(login_url="userauth:login")
def remove_order(request, id):
    order = Order.objects.get(id=id)
    order.is_ordered = False
    order.save()
    return redirect("user_profile:order-track")


@login_required(login_url="userauth:login")
def rewards(request):
    try:
        profile = User_profile.objects.get(user=request.user)
        coupon_collection = CouponUsage.objects.filter(
            user=request.user, is_active=True
        )

    except Order.DoesNotExist:
        profile = None

    context = {
        "profile": profile,
        "coupons": coupon_collection,
    }
    return render(request, "profile/rewards.html", context)


@login_required(login_url="userauth:login")
def wallet(request):
    try:
        profile, created = User_profile.objects.get_or_create(user=request.user)
        wallet, created = Wallet.objects.get_or_create(user=request.user)
        transaction = Transaction.objects.filter(
            user=request.user, wallet=wallet
        ).order_by("-id")

    except Order.DoesNotExist:
        profile = None
        wallet = None
        transaction = None

    context = {"profile": profile, "wallet": wallet, "transcation": transaction}
    return render(request, "profile/wallet.html", context)


@login_required(login_url="userauth:login")
def return_page(request, id):
    order = Order.objects.get(id=id)
    order_product = OrderProduct.objects.filter(order=order, ordered=True).exclude(
        status="Returned"
    )

    context = {"order": order, "order_products": order_product}
    return render(request, "profile/return.html", context)


@login_required(login_url="userauth:login")
def return_order(request, id):
    if request.method == "POST":
        item = request.POST["item"]
        reason = request.POST["cancellation_reason"]
        detail_reason = request.POST["detail_reason"]

        try:
            order = Order.objects.get(id=id)
            order_products = OrderProduct.objects.filter(order=order)

        except Order.DoesNotExist:
            order = None
            order_products = None

        if item == "All":
            order_return = OrderReturn.objects.create(
                user=request.user,
                order=order,
                option=reason,
                reason=detail_reason,
                amount=order.order_total,
            )
            order_return.save()

            order.status = "Return"

            for x in order_products:
                x.status = "Returned"
                x.save()

            order.save()

            subject = "Retun Updation"
            message = f"hello {order.user.username} , Your Return for Order '#{order_return.order.order_number}' has been placed . As soon as our team apporves your return request refund will be credited"
            recipient = order.user.email
            send_mail(
                subject,
                message,
                settings.EMAIL_HOST_USER,
                [recipient],
                fail_silently=False,
            )

            print(f"Order status after update: {order.status}")
            print(f"Order ID: {order.id}")
            print(f"Order products count: {order_products.count()}")

            return redirect("user_profile:order-track")

        elif item != "All":
            product = OrderProduct.objects.get(id=item)
            order_return = OrderReturn.objects.create(
                user=request.user,
                order=order,
                order_product=product,
                option=reason,
                reason=detail_reason,
                amount=product.product.price,
            )

            product.status = "Returned"
            product.save()
            order_return.save()

            subject = "Retun Updation"
            message = f"hello {order.user.username} , Your Return for Product '{order_return.order_product.product.product_name}' has been placed . As soon as our team apporves your refund will be credited"
            recipient = order.user.email
            send_mail(
                subject,
                message,
                settings.EMAIL_HOST_USER,
                [recipient],
                fail_silently=False,
            )

            count = OrderProduct.objects.filter(order=order, status="Returned").count()
            total_products = order_products.count()
            print(f"Order status after update: {order.status}")
            print(f"Order ID: {order.id}")
            print(f"Order products count: {order_products.count()}")
            print(f"Order products count:{count}")
            if count == total_products:
                order.status = "Return"
                order.save()

            return redirect("user_profile:order-track")

    return redirect("user_profile:order-track")


@login_required(login_url="userauth:login")
def returnorder_page(request):
    try:
        order = OrderReturn.objects.filter(collected=False)

    except Order.DoesNotExist:
        order = None
    print(order)
    context = {"orders": order}

    return render(request, "admin/returnedorders.html", context)


@login_required(login_url="userauth:login")
def view_returns(request, id):
    returned = OrderReturn.objects.get(id=id)
    product = OrderProduct.objects.filter(order=returned.order)

    context = {
        "returned": returned,
        "product": product,
    }

    return render(request, "admin/viewreturn.html", context)


@login_required(login_url="userauth:login")
def approve_return(request, id):
    returned = OrderReturn.objects.get(id=id)

    returned.collected = True
    returned.save()

    refund = Wallet.objects.get(user=request.user)
    refund.wallet += returned.amount
    transaction = Transaction()
    transaction.user = request.user
    transaction.wallet = refund
    transaction.amount = returned.amount
    transaction.note = "Order return"
    transaction.transaction = "Cr"

    transaction.save()

    refund.save()

    return redirect("user_profile:returned_page")


@login_required(login_url="userauth:login")
def wishlist(request):
    try:
        profile = User_profile.objects.get(user=request.user)
        wishlist = Wishlist.objects.filter(user=request.user)

    except User_profile.DoesNotExist:
        profile = None

    context = {"profile": profile, "wishlist": wishlist}
    return render(request, "profile/wishlist.html", context)


@login_required(login_url="userauth:login")
def add_wishlist(request, id):
    product = Products.objects.get(id=id)

    if Wishlist.objects.filter(user=request.user, product=product).exists():
        messages.error(request, "This item already exist in the Wishlist")
        return redirect("main:product_details")
    else:
        Wishlist.objects.create(user=request.user, product=product)
        return redirect("user_profile:wishlist")


@login_required(login_url="userauth:login")
def remove_wishlist(request, id):
    wishlist = Wishlist.objects.get(id=id)
    wishlist.delete()
    return redirect("user_profile:wishlist")
