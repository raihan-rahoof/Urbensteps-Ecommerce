import io
from io import BytesIO

from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.db.models import *
from django.http import FileResponse, HttpResponse
from django.shortcuts import redirect, render
from django.views.decorators.cache import never_cache
from orders.models import Order, OrderProduct
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.pdfgen import canvas
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle
from User_auth.models import *

from .models import *

# Create your views here.


def cadmin_login(request):
    try:
        if request.method == "POST":
            username = request.POST.get("username")
            password = request.POST.get("password")

            user = authenticate(username=username, password=password)
            if user and user.is_superuser:
                login(request, user)
                return redirect("adminside:dashboard")
            else:
                messages.error(request, "Invalid Credentials")
                return redirect("adminside:cadmin_login")
        return render(request, "admin/cadmin_login.html")

    except Exception as e:
        print(e)
        return render(request, "404.html")


@login_required(login_url="adminside:cadmin_login")
def cadmin_logout(request):
    logout(request)
    return redirect("adminside:cadmin_login")


@login_required(login_url="adminside:cadmin_login")
def dashboard(request):
    # Query to get the count of each payment type
    try:
        payment_counts = (
            Order.objects.values("payment")
            .annotate(count=Count("payment"))
            .order_by("-count")
        )

        # Extract labels and data for chart.js
        labels = [entry["payment"] for entry in payment_counts]
        data = [entry["count"] for entry in payment_counts]

        specific_statuses = ["Deliverd", "Return", "Cancel"]
        status_counts = (
            Order.objects.filter(status__in=specific_statuses)
            .values("status")
            .annotate(count=Count("status"))
            .order_by("-count")
        )

        # Extract labels and data for product status chart.js
        status_labels = [entry["status"] for entry in status_counts]
        status_data = [entry["count"] for entry in status_counts]

        # Query to get the number of orders per day in a month
        orders_per_day = (
            Order.objects.filter(created_at__month=12, created_at__year=2023)
            .values("created_at__day")
            .annotate(total_amount=Sum("order_total"))
            .order_by("created_at__day")
        )

        # Extract labels and data for line chart.js
        line_labels = [entry["created_at__day"] for entry in orders_per_day]
        line_data = [
            entry["total_amount"] for entry in orders_per_day
        ]  # Fix: Use 'total_amount' instead of 'count'

        context = {
            "labels": labels,
            "data": data,
            "status_labels": status_labels,
            "status_data": status_data,
            "line_labels": line_labels,
            "line_data": line_data,
        }

        return render(request, "admin/dashboard.html", context)
    except Exception as e:
        print(e)
        return render(request, "404.html")


@login_required(login_url="adminside:cadmin_login")
def users_mgmt(request):
    try:
        user = User.objects.exclude(is_superuser=True)
        search = request.GET.get("search")
        if search:
            user = User.objects.filter(
                Q(username__icontains=query) | Q(email__icontains=query)
            )
        context = {"users": user, "search": search}

        return render(request, "admin/users.html", context)
    except Exception as e:
        print(e)
        return render(request, "404.html")


# --------------------user block / unblock---------------------


@login_required(login_url="adminside:cadmin_login")
def user_block(request, user_id):
    try:
        user = User.objects.get(pk=user_id)

        if user.is_active:
            user.is_active = False
            print("000000000000000000000000000000000000")
            user.save()
        return redirect("adminside:users_mgmt")
    except Exception as e:
        print(e)
        return render(request, "404.html")


@login_required(login_url="adminside:cadmin_login")
def user_unblock(request, user_id):
    try:
        user = User.objects.get(pk=user_id)
        if not user.is_active:
            user.is_active = True
            print("111111111111111111111111111111111111111")
            user.save()
        return redirect("adminside:users_mgmt")
    except Exception as e:
        print(e)
        return render(request, "404.html")


# --------------catogory management-----------


@login_required(login_url="adminside:cadmin_login")
def list_category(request):
    try:
        cat_with_counts = Category.objects.annotate(product_count=Count("products"))

        context = {
            "Categories": cat_with_counts,
        }

        return render(request, "admin/list_category.html", context)
    except Exception as e:
        print(e)
        return render(request, "404.html")


@login_required(login_url="adminside:cadmin_login")
def add_category(request):
    try:
        if request.method == "POST":
            category_name = request.POST["name"]
            category_description = request.POST["description"]

            print(category_name)
            print(category_description)
            if Category.objects.filter(name=category_name).exists():
                messages.error(
                    request, "This catogery already Exists,Try adding new one"
                )
                return redirect("adminside:list_category")
            else:
                messages.info(
                    request, f"Sucssesfully added new Category, '{category_name}'"
                )
                new = Category(name=category_name, description=category_description)
                new.save()

        return redirect("adminside:list_category")
    except Exception as e:
        print(e)
        return render(request, "404.html")


@login_required(login_url="adminside:cadmin_login")
def delete_category(request, id):
    try:
        cat = Category.objects.filter(id=id)
        cat.delete()

        return redirect("adminside:list_category")
    except Exception as e:
        print(e)
        return render(request, "404.html")


@login_required(login_url="adminside:cadmin_login")
def show(request, id):
    u = Category.objects.get(id=id)
    offers = Offer.objects.filter(is_active=True)
    context = {"deatails": u, "offers": offers}
    return render(request, "admin/showcategory.html", context)


@login_required(login_url="adminside:cadmin_login")
def update_category(request, id):
    if request.method == "POST":
        category_name = request.POST["name"]
        category_description = request.POST["description"]
        offer = request.POST["offer"]

        # if Category.objects.filter(name=category_name).exists():
        #     messages.error(request, "This Category name already exists")
        #     return redirect("adminside:list_category")
        # else:

        cat = Category(id=id, name=category_name, description=category_description)
        if offer:
            offer_obj = Offer.objects.get(id=offer)
            cat.offer_pro = True
            cat.save()
        else:
            offer_obj = None

        cat.offer = offer_obj
        cat.save()
        messages.info(request, "Sucssesfully edited ")
        return redirect("adminside:list_category")


# -------------------Brand section----------------------------------------------------------------
@login_required(login_url="adminside:cadmin_login")
def list_brand(request):
    try:
        bs = Brand.objects.annotate(total_products=Count("products"))

        context = {
            "brands": bs,
        }

        return render(request, "admin/list_brand.html", context)
    except Exception as e:
        print(e)
        return render(request, "404.html")


@login_required(login_url="adminside:cadmin_login")
def add_brand(request):
    try:
        if request.method == "POST":
            brand_name = request.POST["name"]
            brand_description = request.POST["description"]

            if Category.objects.filter(name=brand_name).exists():
                messages.error(request, "This Brand already Exists,Try adding new one")
                return redirect("adminside:list_category")
            else:
                messages.info(request, f"Sucssesfully added new Brand, '{brand_name}'")
                new = Brand(name=brand_name, description=brand_description)
                new.save()

        return redirect("adminside:list_brand")
    except Exception as e:
        print(e)
        return render(request, "404.html")


@login_required(login_url="adminside:cadmin_login")
def delete_brand(request, id):
    br = Brand.objects.filter(id=id)
    br.delete()

    return redirect("adminside:list_brand")


@login_required(login_url="adminside:cadmin_login")
def show_brand(request, id):
    br = Brand.objects.get(id=id)
    print(br.name)
    context = {"deatails": br}
    return render(request, "admin/brandedit.html", context)


@login_required(login_url="adminside:cadmin_login")
def update_brand(request, id):
    if request.method == "POST":
        brand_name = request.POST["name"]
        brand_description = request.POST["description"]

        if Brand.objects.filter(name=brand_name).exists():
            messages.error(request, "This Brand name already exists")
            return redirect("adminside:list_brand")
        else:
            messages.info(request, "Sucssesfully edited ")

        cat = Brand(id=id, name=brand_name, description=brand_description)
        cat.save()
        return redirect("adminside:list_brand")


# --------------Sales Reprot-----------------------------------------------------


@login_required(login_url="adminside:cadmin_login")
def sales_report(request):
    try:
        start_date = request.GET.get("start_date")
        end_date = request.GET.get("end_date")
        status = request.GET.get("status")

        request.session["start_date"] = start_date
        request.session["end_date"] = end_date
        request.session["status"] = status

        # Filter orders based on provided parameters
        if status == "All":
            filtered_orders = Order.objects.filter(
                created_at__range=[start_date, end_date],
            ).order_by("created_at")
        else:
            filtered_orders = Order.objects.filter(
                created_at__range=[start_date, end_date], status=status
            ).order_by("created_at")

        for order in filtered_orders:
            # Calculate total order amount for each order
            order_items = OrderProduct.objects.filter(order=order)
            order.total_amount = order_items.aggregate(
                total_amount=Sum("product_price")
            )["total_amount"]

            # Add shipping and tax to the total amount
            order.tax = (2 * order.total_amount) / 100
            order.shipping = 20
            order.grand_total = order.total_amount + order.shipping + order.tax

        context = {
            "sales": filtered_orders,
        }

        return render(request, "admin/sales_report.html", context)
    except Exception as e:
        print(e)
        return render(request, "404.html")


@login_required(login_url="adminside:cadmin_login")
def sales_report_pdf(request):
    try:
        start_date = request.session["start_date"]
        end_date = request.session["end_date"]
        status = request.session["status"]

        # Filter orders based on provided parameters
        if status == "All":
            filtered_orders = Order.objects.filter(
                created_at__range=[start_date, end_date],
            ).order_by("created_at")
        else:
            filtered_orders = Order.objects.filter(
                created_at__range=[start_date, end_date], status=status
            ).order_by("created_at")

        for order in filtered_orders:
            # Calculate total order amount for each order
            order_items = OrderProduct.objects.filter(order=order)
            order.total_amount = order_items.aggregate(
                total_amount=Sum("product_price")
            )["total_amount"]

            # Add shipping and tax to the total amount
            order.tax = (2 * order.total_amount) / 100
            order.shipping = 20
            order.grand_total = order.total_amount + order.shipping + order.tax

        # Prepare data for the PDF table
        data = [
            [
                "ID",
                "User",
                "Order Number",
                "Order Date",
                "Status",
                "Total Amount",
                "Tax",
                "Shipping",
                "Grand Total",
            ]
        ]
        for sale in filtered_orders:
            data.append(
                [
                    sale.id,
                    sale.user.username,
                    sale.order_number,
                    sale.created_at,
                    sale.status,
                    sale.total_amount,
                    sale.tax,
                    sale.shipping,
                    sale.grand_total,
                ]
            )

        # Create PDF
        response = HttpResponse(content_type="application/pdf")
        response["Content-Disposition"] = 'attachment; filename="sales_report.pdf"'

        doc = SimpleDocTemplate(response, pagesize=letter)
        table = Table(data)

        # Apply table styles
        style = TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.grey),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
                ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("BOTTOMPADDING", (0, 0), (-1, 0), 12),
                ("BACKGROUND", (0, 1), (-1, -1), colors.beige),
                ("GRID", (0, 0), (-1, -1), 1, colors.black),
            ]
        )

        table.setStyle(style)
        doc.build([table])

        request.session.pop("start_date", None)
        request.session.pop("end_date", None)
        request.session.pop("status", None)

        return response
    except Exception as e:
        print(e)
        return render(request, "404.html")
