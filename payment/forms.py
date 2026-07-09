from django import forms
from .models import ShippingAddress

class ShippingForm(forms.ModelForm):
    shipping_email = forms.CharField(label="", widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'email'}),  required=True)
    shipping_full_name = forms.CharField(label="", widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'full name'}),  required=True)
    shipping_state  = forms.CharField(label="", widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'state'}),  required=True)
    shipping_adress1 = forms.CharField(label="", widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'add1'}),  required=True)
    shipping_address2 = forms.CharField(label="", widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'add2'}),  required=True)
    shipping_zipcode = forms.CharField(label="", widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'zipcode'}),  required=False)
    shipping_country = forms.CharField(label="", widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'country'}),  required=False)
    shipping_city = forms.CharField(label="", widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'city'}),  required=True)

    class Meta:
        model = ShippingAddress
        fields=['shipping_email','shipping_full_name','shipping_state','shipping_adress1','shipping_address2','shipping_zipcode','shipping_country','shipping_city']
        exclude=['user',]



class PaymentForms(forms.Form):
    card_name= forms.CharField(label="", widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Card name'}),  required=True)
    card_number= forms.CharField(label="", widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Card number'}),  required=True)
    card_exp_date= forms.CharField(label="", widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'card expire date'}),  required=True)
    card_cvv_number= forms.CharField(label="", widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'card cvv number'}),  required=True)
    card_address1= forms.CharField(label="", widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Adresss1'}),  required=True)
    card_address2= forms.CharField(label="", widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Address2'}),  required=True)
    card_city= forms.CharField(label="", widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Card city'}),  required=True)
    card_state= forms.CharField(label="", widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Card state'}),  required=True)
    card_zipcode= forms.CharField(label="", widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Card zipcode'}),  required=True)
    card_country= forms.CharField(label="", widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Card country'}),  required=True)


