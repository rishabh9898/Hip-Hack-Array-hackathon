from django.http import HttpResponse
from django.shortcuts import render
from django import forms
from django.contrib.admin.widgets import AdminDateWidget, AdminTimeWidget, AdminSplitDateTime
from django.contrib.auth.models import User
import csv
from django.shortcuts import render, redirect

def index(request):
    return render(request,'pdfreader/landing.html')