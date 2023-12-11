import random
import string


def send_otp(request):
    s = ""
    for x in range(0, 6):
        s += str(random.randint(0, 9))

    request.session["otp"] = s

    return s


def generate_referral_code():
    return "".join(random.choices(string.ascii_uppercase + string.digits, k=6))
