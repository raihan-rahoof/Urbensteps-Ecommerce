# forms.py
from django import forms


class OfferForm(forms.Form):
    name = forms.CharField(max_length=100, required=True)
    description = forms.CharField(widget=forms.Textarea, required=True)
    discount = forms.CharField(max_length=50, required=True)
    start_date = forms.DateField(required=True)
    end_date = forms.DateField(required=True)
