from adminside.models import *
from cart.models import *
from cart.views import _cart_id
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.db.models import *
from django.shortcuts import render,redirect
from offers.models import *
from orders.models import *
from products.models import *

# Create your views here.


# -----------------------home--------------------------------------------------------
def home(request):

        products = Products.objects.filter(is_available=True)
        offer = Offer.objects.filter(is_active=True)
        try:
            cat = Category.objects.get(name="Mens")
            mens = products.filter(category=cat)

        except Category.DoesNotExist:
            mens = None

        try:
            womens_category = Category.objects.get(name="Womens")
            womens_products = products.filter(category=womens_category)
        except Category.DoesNotExist:
            womens_products = None

        try:
            kids_category = Category.objects.get(name="Kids")
            kids_products = products.filter(category=kids_category)
        except Category.DoesNotExist:
            kids_products = None

        try:
            featured_products = products.filter(special=True)
            print(featured_products)
        except Category.DoesNotExist:
            featured_products = None

        context = {
            "products": products,
            "mens": mens,
            "womens": womens_products,
            "kids": kids_products,
            "special": featured_products,
            "offer": offer,
        }
        return render(request, "Home/index.html", context)
   
        



# ----------------------shop page with search---------------------------------------


def shop(request):
    products = Products.objects.filter(is_available=True).order_by("id")
    category = Category.objects.all()
    paginator = Paginator(products, 12)
    page = request.GET.get("page")
    paged_products = paginator.get_page(page)
    search = request.GET.get("search")
    if search:
        paged_products = products.filter(
            Q(product_name__icontains=search)
            | Q(brand__name__icontains=search)
            | Q(category__name__istartswith=search)
        )

    context = {"products": paged_products, "category": category}
    return render(request, "Home/shop.html", context)


# -------------------------product detailed view------------------------------------------


def product_details(request, id):
    product = Products.objects.get(id=id)
    multiimg = MultipleImage.objects.filter(product=id)
    in_cart = Cartitem.objects.filter(
        cart__cart_id=_cart_id(request), product=product
    ).exists()

    sizes = product.sizes.split(",")

    if request.user.is_authenticated:
        try:
            order_product = OrderProduct.objects.filter(
                user=request.user, product_id=product.id, order__status="Deliverd"
            ).exists()
        except order_product.DoesNotExist:
            order_product = None
    else:
        order_product = None

    reviews = ReviewRating.objects.filter(product_id=product.id, status=True)

    context = {
        "product": product,
        "images": multiimg,
        "incart": in_cart,
        "sizes": sizes,
        "order_product": order_product,
        "reviews": reviews,
    }

    return render(request, "Home/details.html", context)


# ------------------------------------------------------------------------------------


def faq(request):
    return render(request, "Home/accordion.html")


def contact(request):
    return render(request, "Home/contact-2.html")
