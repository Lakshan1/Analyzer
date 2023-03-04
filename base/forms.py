from django import forms 
from django.forms import ModelForm
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User 
from .models import *

class CreateUserForm(UserCreationForm):
    class Meta:
        model =User 
        fields = ['username','email','password1','password2']   

    username = forms.CharField(widget=forms.TextInput(attrs={'class':'bg-gray-200 border border-gray-300 h-10 w-10/12 md:w-80 lg:w-80 pl-4 pr-4 ','placeholder':'Username'}))
    email = forms.CharField(widget=forms.TextInput(attrs={'class':'bg-gray-200 border border-gray-300 h-10 w-10/12 md:w-80 lg:w-80 pl-4 pr-4 ','placeholder':'Email'}))
    password1 = forms.CharField(widget=forms.PasswordInput(attrs={'class':'bg-gray-200 border border-gray-300 h-10 w-10/12 md:w-80 lg:w-80 pl-4 pr-4 ','placeholder':'Create Password'}))
    password2 = forms.CharField(widget=forms.PasswordInput(attrs={'class':'bg-gray-200 border border-gray-300 h-10 w-10/12 md:w-80 lg:w-80 pl-4 pr-4 ','placeholder':'Confirm Password'}))


