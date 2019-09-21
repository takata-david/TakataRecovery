from django import forms
from .models import takatarecovery, makemodel

class vinCheckForm(forms.Form):
    vin = forms.CharField(label='', max_length=17, required=False, widget=forms.TextInput(
            attrs={'class' : 'form-control', 'placeholder': 'Enter 17-digit VIN'}))

class detailsForm(forms.Form):
        business_name = forms.CharField(label='', required=False, max_length=50, widget=forms.TextInput(
            attrs={'class': 'form-control', 'placeholder': 'Business Name'}))
        contact_no = forms.IntegerField(label='', required=True, widget=forms.TextInput(
            attrs={'class': 'form-control', 'placeholder': 'Contact Number'}))
        email = forms.EmailField(label='', required=False, widget=forms.TextInput(
            attrs={'class': 'form-control', 'placeholder': 'Email'}))

OEM = [('oem','c')]
MODEL =[('a','b')]
YEAR= [tuple([x,x]) for x in range(1998,2019)]
class makeModelForm(forms.Form):
        oem = forms.CharField(label='OEM', widget=forms.Select(choices=OEM))
        model1 = forms.CharField(label='Model', widget=forms.Select(choices=MODEL))
        year = forms.IntegerField(label='Year', widget=forms.Select(choices=YEAR))
