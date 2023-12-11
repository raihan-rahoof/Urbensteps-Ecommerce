from datetime import date

from django.contrib import messages
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponse
from django.shortcuts import redirect, render
from django.utils import timezone

from .forms import OfferForm
from .models import *

# Create your views here.


def offers(request):
    try:
        offer = Offer.objects.all()
    except ObjectDoesNotExist:
        offer = None
    context = {"offers": offer}
    return render(request, "offers/offers.html", context)


def add_offer(request):
    if request.method == "POST":
        form = OfferForm(request.POST)
        if form.is_valid():
            # Form is valid, process the data
            name = form.cleaned_data["name"]
            description = form.cleaned_data["description"]
            discount = form.cleaned_data["discount"]
            start_date = form.cleaned_data["start_date"]
            end_date = form.cleaned_data["end_date"]

            today = date.today()
            if start_date < today:
                messages.error(request, "Enter the correct Starting date")
                return redirect("offers:offers")
            elif end_date < start_date:
                messages.error(request, "Enter the correct Ending date")
                return redirect("offers:offers")

            offer = Offer(
                name=name,
                description=description,
                discount=discount,
                start_date=start_date,
                end_date=end_date,
            )
            offer.save()

            return redirect("offers:offers")

    return redirect("offers:offers")


def update_offer(request, id):
    if request.method == "POST":
        form = OfferForm(request.POST)
        if form.is_valid():
            # Form is valid, process the data
            name = form.cleaned_data["name"]
            description = form.cleaned_data["description"]
            discount = form.cleaned_data["discount"]
            start_date = form.cleaned_data["start_date"]
            end_date = form.cleaned_data["end_date"]

            today = date.today()
            if start_date < today:
                messages.error(request, "Enter the correct Starting date")
                return redirect("offers:offers")
            elif end_date < start_date:
                messages.error(request, "Enter the correct Ending date")
                return redirect("offers:offers")

            offer = Offer(
                id=id,
                name=name,
                description=description,
                discount=discount,
                start_date=start_date,
                end_date=end_date,
            )

            offer.save()

            return redirect("offers:offers")

    return redirect("offers:offers")


def delete_offer(request, id):
    offer = Offer.objects.get(id=id)
    offer.delete()
    return redirect("offers:offers")
