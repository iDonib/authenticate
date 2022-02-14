from distutils.log import error
from email import message
import imp
import re
from django.conf import settings
from django.forms import PasswordInput
from django.http import HttpResponse
from django.shortcuts import redirect, render
from django.http import HttpResponse
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth import authenticate
from django.contrib.auth import login, logout
from donib import settings
from django.core.mail import send_mail
from django.conf import settings

# Create your views here.
def home(request):
    
    return render(request, "authentication/index.html")

def signup(request):
    if request.method == "POST":
        # username = request.POST.get('username')
        username = request.POST.get('username')
        fname = request.POST.get('fname')
        lname = request.POST.get('lname')
        email = request.POST.get('email')
        pass1 = request.POST.get('pass1')
        pass2 = request.POST.get('pass2')

        # if User.objects.filter(username=username):
        #     messages.error(request, 'Username already taken! Choose some other username!')
        #     return redirect('home')
        
        # if User.objects.filter(email=email):
        #     messages.error(request, "This Email is already registered")
        #     return redirect('home')
        
        if len(username)>10:
            messages.error(request, "Only 10 or less characters for username")

        if pass1 != pass2:
            messages.error(request, "Passwords did not match")
        
        if not username.isalnum():
            messages.error(request, 'Username must only contains alphabets and numbers')
            return redirect('home')


        myuser = User.objects.create_user(username, email, pass1)
        myuser.first_name = fname
        myuser.last_name = lname

        myuser.save()

        messages.success(request, "Your account has been created successfully! \n Please check your email for confirming your account!")

        # Welcome Email
        subject = "Welcome to Donib's Login!"
        message = "Hello " + myuser.first_name + "!! \n" + "Welcome to Donib's page!! \n Thank yu for visiting my site \n We have sent you a confirmation email. Please confirm your email address in order to activate your account. \n\n Regards,\n Donib"
        from_email = settings.EMAIL_HOST_USER
        to_list = [myuser.email]
        send_mail(subject, message, from_email, to_list, fail_silently=True)

        return redirect('signin')
        
    return render(request, "authentication/signup.html")

def signin(request):
    if request.method == "POST":
        username = request.POST.get('username')
        pass1 = request.POST.get('pass1')

        user = authenticate(username=username, password=pass1)

        if user is not None:
            login(request, user)
            fname = user.first_name
            return render(request, "authentication/index.html", {'fname':fname})

        else:
            messages.error(request, "Bad Credentials")
            return redirect("home") #check

    return render(request, "authentication/signin.html")

def signout(request):
    logout(request)
    messages.success(request, "Signed Out Successfully!")
    return redirect('home')