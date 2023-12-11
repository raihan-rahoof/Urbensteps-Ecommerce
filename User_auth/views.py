from adminside.models import *
from cart.models import *
from cart.views import _cart_id
from django.conf import settings
from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User, auth
from django.contrib.auth.tokens import default_token_generator
from django.contrib.sites.shortcuts import get_current_site
from django.core.exceptions import ObjectDoesNotExist
from django.core.mail import send_mail
from django.http import HttpResponse
from django.shortcuts import redirect, render
from django.template.loader import render_to_string
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from products.models import Products
from user_profile.models import *

from .models import *
from .utils import *

# ---------------------------User login ------------------------------------------------------


def user_login(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        if not username or not password:
            messages.error(
                request, "All fields are required. Please fill in all required fields."
            )
            return redirect("userauth:login")

        user = authenticate(username=username, password=password)

        if user is not None:
            if user.is_active:
                try:
                    cart = Cart.objects.get(cart_id=_cart_id(request))
                    is_cart_item_exists = Cartitem.objects.filter(cart=cart).exists()
                    if is_cart_item_exists:
                        cart_item = Cartitem.objects.filter(cart=cart)

                        for item in cart_item:
                            item.user = user
                            item.save()

                except:
                    pass
                print("0000000000000000000000!!!!!!!!!!!")
                login(request, user)
                return redirect("main:home")
            else:
                print("aksje;jawq30495-20934ijwep9rq904!!!!!!!!!!!")
                messages.error(
                    request, "Your account has been blocked due to some reason"
                )
                return redirect("userauth:login")
        else:
            messages.error(request, "Invalid credentials")
            return redirect("userauth:login")
    else:
        return render(request, "auth/login.html")


# ----------------------------User registeration-----------------------------------------------------------------
def user_register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]
        gender = request.POST["gender"]
        password1 = request.POST["password1"]
        password2 = request.POST["password2"]
        refferal = request.POST["refferal_code"]

        # stored in session to authenticate when the otp verifys
        request.session["username"] = username
        request.session["email"] = email
        request.session["password"] = password1
        request.session["gender"] = gender

        # checking the refferal for eg: if there is refferal code or not
        if refferal:
            try:
                refferer = Custom_user.objects.get(refferal_code=refferal)
            except ObjectDoesNotExist:
                refferer = None

            if refferer:
                request.session["refferal"] = refferal
            else:
                messages.info(request, "Refferal code not valid")
                return redirect("userauth:register")

        if not username or not email or not gender or not password1 or not password2:
            messages.error(
                request, "All fields are required. Please fill in all required fields."
            )
            return redirect("userauth:register")

        if password1 == password2:
            if User.objects.filter(username=username).exists():
                messages.info(request, "Username already Exist")
                return redirect("userauth:register")
            elif User.objects.filter(email=email).exists():
                messages.info(request, "Email already Exist")
                return redirect("userauth:register")
            else:
                otp_print = send_otp(request)
                print(otp_print)
                subject = "Email verigication"
                message = f"hello {username} , your otp is {otp_print}"
                recipient = email
                send_mail(
                    subject,
                    message,
                    settings.EMAIL_HOST_USER,
                    [recipient],
                    fail_silently=False,
                )
                return redirect("userauth:otp")
        else:
            messages.info(request, "password mismatch")
            return redirect("userauth:register")

    return render(request, "auth/register.html")


# ---------------------Otp verification veiw --------------------------------------------------
def verify_otp(request):
    refferer = None
    if request.method == "POST":
        otp_ = request.POST.get("otp")

        if "refferal" in request.session:
            refferer = Custom_user.objects.get(
                refferal_code=request.session["refferal"]
            )
            wallet, created = Wallet.objects.get_or_create(user=refferer)
            request.session["refferer"] = refferer
            if created:
                wallet.wallet = 0  # Optional: Setting wallet to 0 may not be necessary
                wallet.user = refferer

            wallet.wallet += 40
            wallet.save()

            # Create a Transaction object for the referral bonus
            Transaction.objects.create(
                user=refferer,
                wallet=wallet,
                amount=40,
                note="Referral bonus for referred user",
                transaction="Cr",
            )

        if otp_ == request.session["otp"]:
            # getting all the details stored in sessions
            user = Custom_user.objects.create_user(
                username=request.session["username"],
                refferal_code=generate_referral_code(),
                refferer=refferer if "refferal" in request.session else None,
                email=request.session["email"],
                password=request.session["password"],
                gender=request.session["gender"],
                is_block=False,
            )
            user.save()

            # checking if there is a reffer or not
            refferish = Custom_user.objects.get(username=request.session["username"])
            if refferish.refferer:
                new_user_wallet, _ = Wallet.objects.get_or_create(user=user)
                new_user_wallet.wallet += 40
                new_user_wallet.save()

                Transaction.objects.create(
                    user=user,
                    wallet=new_user_wallet,
                    amount=40,
                    note="Referral bonus for registration",
                    transaction="Cr",
                )

            request.session.flush()

            print("user created !!!!!!!!!!!")
            return redirect("userauth:login")
        else:
            messages.info(request, "OTP doesn't match")
            return redirect("userauth:otp")

    return render(request, "auth/otp.html")


# ------------------User logout View -----------------------------------------
def user_logout(request):
    auth.logout(request)
    return redirect("main:home")


# -----------------Forgot password ----------------------------------------------
def forgot_password(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]
        if User.objects.filter(username=username).exists():
            user = User.objects.get(username=username)
            if user.email == email:
                current_site = get_current_site(request)
                subject = "Reset your Password"
                message = render_to_string(
                    "auth/reset_password.html",
                    {
                        "user": user,
                        "domain": current_site,
                        "uid": urlsafe_base64_encode(force_bytes(user.pk)),
                        "token": default_token_generator.make_token(user),
                    },
                )
                recipient = email
                send_mail(
                    subject,
                    message,
                    settings.EMAIL_HOST_USER,
                    [recipient],
                    fail_silently=False,
                )

                messages.success(request, "Reset email has been sented to your email")
                return redirect("userauth:forgot_password")
            else:
                messages.error(request, "This email is not associated with this user")
                return redirect("userauth:forgot_password")

        else:
            messages.error(request, "Account does not exist")
            return redirect("userauth:forgot_password")

    return render(request, "auth/forgot.html")


def resetpassword_validate(request, uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        request.session["uid"] = uid
        messages.success(request, "please reset your password")
        return redirect("userauth:reset_password")
    else:
        messages.error(request, "This link has been expired")
        return redirect("userauth:login")


def reset_password(request):
    if request.method == "POST":
        password = request.POST["password"]
        confirm_password = request.POST["confirm-password"]

        if password == confirm_password:
            uid = request.session.get("uid")
            user = User.objects.get(pk=uid)
            user.set_password(password)
            user.save()
            messages.success(request, "Password changed sucssesfully")
            return redirect("userauth:login")
        else:
            messages.error(request, "Password do not match")
            return redirect("userauth:reset_password")
    else:
        return render(request, "auth/changepassword.html")


# ------------------- django Oauth-------------------------------


def signup_redirect(request):
    messages.error(request, "Something went wrong , Try with another account ")
    return redirect("userauth:login")
