from django import forms
from .models import takatarecovery, makemodel
import pandas as pd

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


YEAR= [tuple([x,x]) for x in range(1998,2019)]
class makeModelForm(forms.Form):
    locatedQuery = makemodel.objects.values('id', 'oem', 'model', 'year')
    located = pd.DataFrame(locatedQuery)

    oem1 = located['oem'].unique()
    OEM = [tuple([o,o]) for o in oem1]

    model0 = located['model'].unique()
    MODEL =[tuple([m,m]) for m in model0]

    oem = forms.CharField(label='OEM', required=False, widget=forms.Select(choices=OEM))
    model1 = forms.CharField(label='Model', required=False, widget=forms.Select(choices=MODEL))
    year = forms.IntegerField(label='Year', required=False, widget=forms.Select(choices=YEAR))


class makeModelCheck(forms.ModelForm):
    class Meta:
        fields = ['oem', 'model', 'year']
