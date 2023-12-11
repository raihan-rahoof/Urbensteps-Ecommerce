from adminside.models import Category
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import *
from django.http import HttpResponse
from django.shortcuts import redirect, render

from .models import *

# Create your views here.


@login_required(login_url="adminside:cadmin_login")
def manage_products(request):
    products = Products.objects.all()
    search = request.GET.get("search")

    if search:
        # Use Q objects to perform case-insensitive search
        products = Products.objects.filter(
            Q(product_name__icontains=search)
            | Q(brand__name__icontains=search)
            | Q(  # Use brand__name__icontains to search for brand name
                category__name__icontains=search
            )  # Use category__name__icontains to search for category name
        )

    context = {
        "products": products,
    }

    return render(request, "products/products.html", context)


@login_required(login_url="adminside:cadmin_login")
def add_products(request):
    brands = Brand.objects.filter(is_available=True)
    categories = Category.objects.filter(is_available=True)
    offers = Offer.objects.filter(is_active=True)
    context = {"categories": categories, "brands": brands, "offers": offers}

    if request.method == "POST":
        product_name = request.POST["product_name"]
        category = request.POST["category"]
        sub_category = request.POST["sub_category"]
        description = request.POST["description"]
        stocks = request.POST["stocks"]
        sizes = request.POST["sizes"]
        brand = request.POST["brand"]
        price = request.POST["price"]
        return_time = request.POST["return"]
        material = request.POST["material"]
        warranty = request.POST["warranty"]
        offer = request.POST.get("offer", None)
        product_img = request.FILES.get("product_image")
        additional_images = request.FILES.getlist("additional_images")
        special = request.POST.get("special", False)
        offer_pro = request.POST.get("has_offer")

        if "special" in request.POST:
            special = request.POST["special"] == "on"
        else:
            special = False

        if (
            not product_name
            or not category
            or not description
            or not stocks
            or not sizes
            or not brand
            or not price
        ):
            messages.error(request, "All required fields must be filled.")
            return redirect("products:add_products")

        if Products.objects.filter(product_name=product_name).exists():
            messages.info(request, "Product with this name already exists !!")

        elif not product_img or not additional_images:
            messages.error(request, "Product image and additional images are required.")

        else:
            if len(additional_images) < 3:
                messages.error(
                    request, "You can upload a maximum of three additional images."
                )

            else:
                cat = Category.objects.get(id=category)
                br = Brand.objects.get(id=brand)
                offer_item = None
                if offer:
                    offer_item = Offer.objects.get(id=offer)
                product = Products(
                    product_name=product_name,
                    category=cat,
                    subcategory=sub_category,
                    description=description,
                    stock=stocks,
                    sizes=sizes,
                    brand=br,
                    offer=offer_item,
                    price=price,
                    return_time=return_time,
                    meterial=material,
                    warranty=warranty,
                    image=product_img,
                    special=special,
                )
                product.save()

                if offer:
                    product.offer_pro = True
                    product.save()

                for image in additional_images:
                    print(image, "image")
                    additional_image = MultipleImage.objects.create(
                        product=product, images=image
                    )
                    additional_image.save()
                messages.info(request, "Product added sucssesfully ")

                return redirect("products:manage_products")

    return render(request, "products/addproducts.html", context)


@login_required(login_url="adminside:cadmin_login")
def remove_product(request, id):
    product = Products.objects.get(id=id)
    if product.is_available:
        product.is_available = False
    else:
        product.is_available = True

    product.save()
    return redirect("products:manage_products")


@login_required(login_url="adminside:cadmin_login")
def delete_product(request, id):
    product = Products.objects.get(id=id)
    product.delete()
    return redirect("products:manage_products")


@login_required(login_url="adminside:cadmin_login")
def edit_product(request, id):
    product = Products.objects.get(id=id)
    category = Category.objects.all()
    brand = Brand.objects.all()
    offers = Offer.objects.all()

    context = {
        "product": product,
        "categories": category,
        "brand": brand,
        "offers": offers,
    }

    return render(request, "products/editproducts.html", context)


@login_required(login_url="adminside:cadmin_login")
def update_product(request, id):
    if request.method == "POST":
        product_name = request.POST["product_name"]
        category = request.POST["category"]
        sub_category = request.POST["sub_category"]
        description = request.POST["description"]
        stocks = request.POST["stocks"]
        sizes = request.POST["sizes"]
        brand = request.POST["brand"]
        offer = request.POST["offer"]
        price = request.POST["price"]
        return_time = request.POST["return"]
        material = request.POST["material"]
        warranty = request.POST["warranty"]
        product_img = request.FILES.get("product_image")
        additional_images = request.FILES.getlist("additional_images")

        if product_img:
            product = Products.objects.get(id=id)
            cat = Category.objects.get(id=category)
            br = Brand.objects.get(id=brand)
            if offer:
                offer_obj = Offer.objects.get(id=offer)
                product.offer_pro = True
                product.save()
            else:
                offer_obj = None

            product.offer = offer_obj
            product.product_name = product_name
            product.category = cat
            product.sub_category = sub_category
            product.description = description
            product.stock = stocks
            product.sizes = sizes
            product.brand = br
            product.price = price
            product.return_time = return_time
            product.meterial = material
            product.warranty = warranty
            product.image = product_img

            product.save()

        else:
            product = Products.objects.get(id=id)
            cat = Category.objects.get(id=category)
            br = Brand.objects.get(id=brand)
            if offer:
                offer_obj = Offer.objects.get(id=offer)
                product.offer_pro = True
                product.save()
            else:
                offer_obj = None
            product.offer = offer_obj
            product.product_name = product_name
            product.category = cat
            product.sub_category = sub_category
            product.description = description
            product.stock = stocks
            product.sizes = sizes
            product.brand = br
            product.price = price
            product.return_time = return_time
            product.meterial = material
            product.warranty = warranty

            product.save()

        if additional_images:
            product.multipleimage_set.all().delete()

            for image in additional_images:
                multi_images = MultipleImage(product=product, images=image)
                multi_images.save()

        messages.success(request, "Product edited Sucssesfully")

        return redirect("products:manage_products")


@login_required(login_url="adminside:cadmin_login")
def view_product(request, id):
    product = Products.objects.get(id=id)
    multiimg = MultipleImage.objects.filter(product=id)
    context = {"product": product, "images": multiimg}
    return render(request, "products/viewproducts.html", context)
