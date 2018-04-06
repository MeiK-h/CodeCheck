from django import forms
from django.core.exceptions import ValidationError

from .models import Bark


class BarkForm(forms.Form):
    title = forms.CharField(max_length=200)
    language = forms.CharField(max_length=200)
