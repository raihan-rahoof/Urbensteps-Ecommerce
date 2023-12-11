from django import forms
from django_recaptcha.fields import ReCaptchaField
from .models import *

class FormWithCaptcha(forms.Form):
    captcha = ReCaptchaField()



class ReviewForm(forms.ModelForm):
    class Meta:
        model = ReviewRating
        fields = ['review','rating']

        