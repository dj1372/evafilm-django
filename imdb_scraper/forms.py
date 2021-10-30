from django import forms
from django.forms import fields

class GetLinkForm(forms.Form):
    url = forms.CharField(label='url', max_length=255)


class GetMultiLinkForm(forms.Form):
    multi_url = forms.CharField(label='url', max_length=255)