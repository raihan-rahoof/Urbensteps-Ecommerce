from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render
from orders.models import *


# Create your views here.
@login_required(login_url="adminside:cadmin_login")
def coupons(request):
    coupons = Coupons.objects.all()

    context = {
        "coupons": coupons,
    }

    return render(request, "admin/coupons.html", context)


@login_required(login_url="adminside:cadmin_login")
def add_coupon(request):
    if request.method == "POST":
        coupon_name = request.POST["name"]
        description = request.POST["description"]
        code = request.POST["code"]
        amount = request.POST["min_amount"]
        discount = request.POST["discount"]
        pic = request.FILES.get("pic")

        if Coupons.objects.filter(name=coupon_name).exists():
            messages.error(request, "This Coupon already Exists,Try adding new one")
            return redirect("coupons:coupons")
        elif Coupons.objects.filter(code=code).exists():
            messages.error(request, "This Code already Exists,Try adding new one")
            return redirect("coupons:coupons")
        elif int(discount) > 80:
            messages.error(
                request, "This Discount percentage is Very high currently not available"
            )
            return redirect("coupons:coupons")

        else:
            messages.info(request, f"Sucssesfully added new Coupon, '{coupon_name}'")
            new = Coupons(
                name=coupon_name,
                code=code,
                description=description,
                min_amount=amount,
                discount=discount,
                image=pic,
            )
            new.save()

    return redirect("coupons:coupons")


@login_required(login_url="adminside:cadmin_login")
def delete_coupon(request, id):
    coupon = Coupons.objects.get(id=id)
    coupon.delete()

    return redirect("coupons:coupons")


@login_required(login_url="adminside:cadmin_login")
def disable_coupon(request, id):
    coupon = Coupons.objects.get(id=id)
    if coupon.is_active:
        coupon.is_active = False
    else:
        coupon.is_active = True
    coupon.save()
    usage = CouponUsage.objects.get(coupon=coupon)
    if usage.is_active:
        usage.is_active = False
    else:
        usage.is_active = True

    usage.save()

    return redirect("coupons:coupons")


@login_required(login_url="adminside:cadmin_login")
def edit_coupon(request, id):
    if request.method == "POST":
        coupon_name = request.POST["name"]
        description = request.POST["description"]
        code = request.POST["code"]
        amount = request.POST["min_amount"]
        discount = request.POST["discount"]
        pic = request.FILES.get("pic")

        if int(discount) > 80:
            messages.error(
                request, "This Discount percentage is Very high currently not available"
            )
            return redirect("coupons:coupons")

        # Retrieve the existing coupon
        existing_coupon = Coupons.objects.get(id=id)

        # Update the fields that are not dependent on the image
        existing_coupon.name = coupon_name
        existing_coupon.code = code
        existing_coupon.description = description
        existing_coupon.min_amount = amount
        existing_coupon.discount = discount

        # Check if a new image has been provided
        if pic:
            existing_coupon.image = pic

        # Save the updated coupon
        existing_coupon.save()

        messages.info(request, f"Successfully edited the Coupon '{coupon_name}'")
        return redirect("coupons:coupons")
    else:
        return redirect("coupons:coupons")
