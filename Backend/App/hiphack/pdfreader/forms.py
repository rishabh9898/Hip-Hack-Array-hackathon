from django import forms
from .models import Reader
from django.core import validators

class CreateForm(forms.ModelForm):
   export_to_CSV = forms.BooleanField(required=False)
   class Meta:
     model = Reader
     fields = ['search','name','amount']
# 	email=forms.CharField(error_messages={'required':'Enter your email'})
# 	password= forms.CharField(widget=forms.PasswordInput,error_messages={'required':'Enter your password'})
