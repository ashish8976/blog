from django.shortcuts import render,redirect
from django.http import HttpResponse
from django.db.models import Q
from django.contrib.auth.hashers import make_password
from django.contrib.auth.hashers import check_password
from django.core.mail import send_mail
from django.conf import settings
import random
from . models import User, Post
import time

# Create your views here.

def register(request):
    if request.method =="POST":
        if User.objects.filter(email=request.POST['email']).exists():
            return render(request, 'register.html', {'msg': 'Email already exists'})
    
        if User.objects.filter(username=request.POST['username']).exists():
            return render(request, 'register.html', {'msg': 'Username already taken, please choose another'})
        
        if request.POST['password'] != request.POST['cpassword']:
            return render(request,'register.html',{'msg','password and confirm password not match'})
        
        User.objects.create(
            fname=request.POST['fname'],
            lname=request.POST['lname'],
            username=request.POST['username'],
            email=request.POST['email'],
            password=make_password(request.POST['password']),
            role=request.POST['role'],
            profile_photo=request.FILES.get('profile_photo'),
        )
        return render(request, 'login.html', {'msg': 'Registration Successful!'})
    else:
        return render (request,'register.html')




def login(request):
    if request.method == "POST":
        login_input = request.POST['username']
        login_password = request.POST['password']

        try:
            user = User.objects.get(Q(username=login_input) | Q(email=login_input))

            if check_password(login_password,user.password):
                request.session['user_email']=user.email
                request.session['user_name'] = user.username
                request.session['user_role'] = user.role
                request.session['user_image'] = user.profile_photo.url if user.profile_photo else None
                return redirect('index')
            else:
                return render(request, 'login.html', {'msg':"Password is not correct"})
        except User.DoesNotExist:
            return render(request, 'login.html', {'msg':"User not found"})
    else:
        return render(request,'login.html')
    


def logout(request):
    request.session.flush()
    return render(request,'login.html')

def author(request):
    return render(request,'author.html')

def forgetpassword(request):
    if request.method == "POST":
        email = request.POST.get('email')
        try:
            user = User.objects.get(email=email)
            otp = random.randint(100001,999999)
            subject = "OTP for forget Password"
            message =f"Hi {user.fname}  {user.lname}  Your OTP  is { str(otp)}"
            email_from = settings.EMAIL_HOST_USER
            recipient_list = [user.email,]
            send_mail(
                subject,
                message,
                email_from,
                recipient_list,
                fail_silently=False,
            )
            request.session['useremail'] = user.email
            request.session['otp'] = str(otp)
            request.session['otp_time'] = time.time()
            return redirect('otp')
        except User.DoesNotExist:
            msg = "Email  does not Exists"
            return render (request, 'forgetpassword.html',{'msg':msg})
    else:
        return render(request,'forgetpassword.html')
    

def otp(request):
    if request.method == "POST":
          #   user = User.objects.get(email = request.session['newemail'])
          
            entered_otp = request.POST.get('uotp')
            session_otp = request.session.get('otp')
            otp_time = request.session.get('otp_time')

            if not session_otp or not otp_time:
                msg = "Session expired. Try again."
                return render(request, 'otp.html', {'msg': msg})
            
            if entered_otp == session_otp:
                del request.session['otp']
                del request.session['otp_time']
                return redirect('resetpassword') 
            
            else:
                 msg = "OTP is invalid"
                 return render(request, 'otp.html', {'msg': msg})
    else:
        return render(request, 'otp.html')

def resetpassword(request):
    if request.method == "POST":
        update_email = request.session.get('useremail')

        if not update_email:
            return redirect ('forgetpassword')
        
        try:
             user = User.objects.get(email = update_email)
             new_password = request.POST.get('newpassword')
             cpassword = request.POST.get('cpassword')

             if new_password == cpassword :
                user.password = make_password(new_password)
                user.save()
                del request.session['useremail']
                return redirect('login')
             else:
                    msg = "Password and Confirm Password doesn't match"
                    return render(request,'resetpassword.html',{'msg':msg})
        except User.DoesNotExist:
            msg = "User not Found"
            return render(request,'forget_password.html')
    else:
        return render(request,'resetpassword.html')
    
def index(request):
    return render (request,'index.html')

def explore(request):
    return render (request,'explore.html')

def blog_details(request):
    return render (request,'blog_details.html')

def category(request):
    return render(request,'category.html')


def dashboard(request):
    return render (request, 'dashboard.html')


def create_post(request):
    if request.method == "POST":
        Post.objects.create(
            post_title = request.POST.get('post_title'),
            post_desc = request.POST.get('post_desc'),
            post_category = request.POST.get('post_category'),
            tags = request.POST.get('tags'),
            post_image = request.FILES.get('post_image')
        )
        return redirect('dashboard')
        
    return render(request,'create_post.html')



def profile(request):
     user = User.objects.get(email=request.session['user_email'])
     if request.method == "POST":
        if request.POST.get('fname'):
             user.fname = request.POST.get('fname')
        if request.POST.get('lname'):
            user.lname = request.POST.get('lname')
        if request.POST.get('username'):
            user.username = request.POST.get('username')
        if request.POST.get('email'):
            user.email = request.POST.get('email')
        if request.POST.get('role'):
            user.role = request.POST.get('role')
        if request.POST.get('bio'):
            user.bio = request.POST.get('bio')
        if request.POST.get('profile_photo'):
            user.profile_photo = request.POST.get('profile_photo')

        return redirect('profile')
     
     return render(request, 'profile.html')
def edit_profile(request):
    return render(request, 'edit_profile.html')
        
def author_story(request):
    return render(request, 'author_story.html')
