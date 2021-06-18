from django import forms
from .models import Reader
from django.core import validators

class CreateForm(forms.Form):
	PDF = forms.FileField(widget=forms.FileInput(attrs={'class': 'pdfclass'}))
	# image = forms.FileField(widget=forms.FileInput(attrs={'class': 'imageclass'}))
	# video = forms.FileField(widget=forms.FileInput(attrs={'class': 'videoclass'}))
	fields = ['PDF','image','video']

# 3 minutes to load
