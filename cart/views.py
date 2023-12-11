from decimal import Decimal

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST
from offers.models import *
from products.models import *

from .models import *

# Create your views here.


def _cart_id(request):
    cart = request.session.session_key
    if not cart:
        cart = request.session.create()
    return cart


def cart(request, total=0, quantity=0, cart_items=None):
    try:
        tax = 0
        grand_total = 0
        shipping = 0
        if not request.user.is_authenticated:
            cart = Cart.objects.get(cart_id=_cart_id(request))
            print(cart.cart_id, "caridfaklds")
            cart_items = Cartitem.objects.filter(cart=cart, is_active=True)
        else:
            cart_items = Cartitem.objects.filter(user=request.user, is_active=True)

        for cart_item in cart_items:
            product_price = cart_item.product.price
            product_offer = cart_item.product.offer
            category_offer = cart_item.product.category.offer

            if product_offer is None and category_offer is None:
                total += cart_item.product.price * cart_item.quantity
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
        "tax": tax,
        "shipping": shipping,
        "grandtotal": grand_total,
    }

    return render(request, "cart/cart.html", context)


def add_cart(request, id):
    print(id, "id")
    product = Products.objects.get(id=id)
    if not request.user.is_authenticated:
        try:
            cart = Cart.objects.get(cart_id=_cart_id(request))
        except Cart.DoesNotExist:
            cart = Cart.objects.create(cart_id=_cart_id(request))

        cart.save()
        try:
            cart_item = Cartitem.objects.get(product=product, cart=cart)
            cart_item.quantity += 1
            cart_item.save()
        except Cartitem.DoesNotExist:
            cart_item = Cartitem.objects.create(
                product=product,
                quantity=1,
                cart=cart,
            )
            cart_item.save()

        return redirect("cart:cart")

    else:
        try:
            cart_item = Cartitem.objects.get(product=product, user=request.user)
            cart_item.quantity += 1
            cart_item.save()
        except Cartitem.DoesNotExist:
            cart_item = Cartitem.objects.create(
                user=request.user,
                product=product,
                quantity=1,
            )
            cart_item.save()

        return redirect("cart:cart")


def update_cart(request):
    if request.method == "POST":
        try:
            product_id = int(request.POST.get("product_id"))
            action = request.POST.get("action")
            product_qty = int(request.POST.get("quantity", 0))

            cart_item = get_object_or_404(
                Cartitem, user=request.user, product_id=product_id
            )

            if product_qty == 0:
                return redirect("cart:cart")

            if product_qty > cart_item.product.stock:
                return JsonResponse(
                    {"status": "Requested quantity exceeds available quantity"}
                )

            cart_item.quantity = product_qty
            cart_item.save()

            if not request.user.is_authenticated:
                cart = Cart.objects.get(cart_id=_cart_id(request))
                cart_items = Cartitem.objects.filter(cart=cart, is_active=True)
            else:
                cart_items = Cartitem.objects.filter(user=request.user, is_active=True)

            total = 0
            quantity = 0

            for cart_item in cart_items:
                product_price = float(cart_item.product.price)
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

                    discount_price = (discount / 100) * product_price
                    discounted_price = product_price - discount_price

                    total += discounted_price * cart_item.quantity
                    quantity += cart_item.quantity

            tax = (2 * total) / 100
            shipping = 20
            grand_total = total + shipping + tax

            single_price = product_price * cart_item.quantity

            return JsonResponse(
                {
                    "status": "Cart Updated Successfully",
                    "single_price": single_price,
                    "grand_total": grand_total,
                    "tax": tax,
                    "shipping": shipping,
                }
            )
        except ObjectDoesNotExist:
            pass

    return JsonResponse({"status": "Invalid request method"})


def remove_cart(request, id):
    if not request.user.is_authenticated:
        cart = Cart.objects.get(cart_id=_cart_id(request))
        product = get_object_or_404(Products, id=id)
        cart_item = Cartitem.objects.get(product=product, cart=cart)

        if cart_item.quantity > 1:
            cart_item.quantity -= 1
            cart_item.save()
        else:
            cart_item.delete()
        return redirect("cart:cart")
    else:
        product = get_object_or_404(Products, id=id)
        cart_item = Cartitem.objects.get(product=product, user=request.user)

        if cart_item.quantity > 1:
            cart_item.quantity -= 1
            cart_item.save()
        else:
            cart_item.delete()
        return redirect("cart:cart")


def delete_cart_item(request, id):
    if not request.user.is_authenticated:
        cart = Cart.objects.get(cart_id=_cart_id(request))
        product = get_object_or_404(Products, id=id)
        cart_item = Cartitem.objects.get(product=product, cart=cart)
        cart_item.delete()

        return redirect("cart:cart")
    else:
        product = get_object_or_404(Products, id=id)
        cart_item = Cartitem.objects.get(product=product, user=request.user)
        cart_item.delete()

        return redirect("cart:cart")
