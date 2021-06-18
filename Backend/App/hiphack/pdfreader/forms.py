from django import forms
from .models import Reader
from django.core import validators

class CreateForm(forms.ModelForm):
	file1 = forms.FileField(widget=forms.FileInput(attrs={'class': 'file1class'}))
	class Meta:
		model = Reader
		fields = ['search','file1']
# 	email=forms.CharField(error_messages={'required':'Enter your email'})
# 	password= forms.CharField(widget=forms.PasswordInput,error_messages={'required':'Enter your password'})
