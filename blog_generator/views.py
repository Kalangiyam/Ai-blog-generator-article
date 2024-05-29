from django.shortcuts import render,redirect
from django.contrib.auth import decorators,login,logout
# from django.contrib.admin import

# Create your views here.
def index(request):
    return render(request,'home.html')

def user_login(request):
    return render(request,'login.html')

def user_signup(request):
    return render(request,'signup.html')

def user_logout(request):
    pass

