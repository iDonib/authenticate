from base64 import urlsafe_b64encode
from distutils.log import error
from email import message
import imp
from lib2to3.pgen2.tokenize import generate_tokens
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
from django.core.mail import EmailMessage, send_mail
from django.conf import settings
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_text
from . tokens import generate_token

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

        if User.objects.filter(username=username):
            messages.error(request, 'Username already taken! Choose some other username!')
            return redirect('home')
        
        if User.objects.filter(email=email):
            messages.error(request, "This Email is already registered")
            return redirect('home')
        
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
        myuser.is_active = False
        myuser.save()

        messages.success(request, "Your account has been created successfully! \n Please check your email for confirming your account!")

        # Welcome Email
        subject = "Welcome to Donib's Login!"
        message = "Hello " + myuser.first_name + "!! \n" + "Welcome to Donib's page!! \n Thank yu for visiting my site \n We have sent you a confirmation email. Please confirm your email address in order to activate your account. \n\n Regards,\n Donib"
        from_email = settings.EMAIL_HOST_USER
        to_list = [myuser.email]
        send_mail(subject, message, from_email, to_list, fail_silently=True)

        # Email Confirmation email

        current_site = get_current_site(request)
        email_subject = "Confirm your email at Donib's Page!"
        message2 = render_to_string("email_confirmation.html", {
            'name': myuser.first_name,
            'domain': current_site.domain,
            'uid': urlsafe_base64_encode(force_bytes(myuser.pk)),
            'token': generate_token.make_token(myuser)
        })

        email = EmailMessage(
            email_subject,
            message2,
            settings.EMAIL_HOST_USER,
            [myuser.email],
        )
        email.fail_silently = True
        email.send()

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

def activate(request, uidb64, token):
    try:
        uid = force_text(urlsafe_base64_decode(uidb64))
        myuser = User.objects.get(pk=uid)
    except(TypeError, ValueError, OverflowError, User.DoesNotExist):
        myuser = None

    if myuser is not None and generate_token.check_token(myuser, token):
        myuser.is_active = True
        myuser.save()
        login(request, myuser)
        return redirect('home')
    else:
        return render(request, 'activation_failed.html')
