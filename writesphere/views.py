from django.shortcuts import render,redirect
from django.http import HttpResponse
from django.db.models import Q
from django.contrib.auth import login as auth_login
from django.contrib.auth import logout as auth_logout
from django.core.mail import send_mail
from django.conf import settings
import random
from . models import *
import time
from functools import wraps
from django.contrib.auth.decorators import login_required
from .form import * 



def session_required(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.session.get('user_email'):
            return redirect('login')
        return view_func(request, *args, **kwargs)
    return wrapper


def author_required(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.session.get('user_email'):
            return redirect('login')
        if request.session.get('user_role') != 'Author':
            return redirect('index')  
        return view_func(request, *args, **kwargs)
    return wrapper


def reader_required(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.session.get('user_email'):
            return redirect('login')
        if request.session.get('user_role') != 'Reader':
            return redirect('index')  
        return view_func(request, *args, **kwargs)
    return wrapper


def register(request):
    form = RegistrationForm()
    if request.method =="POST":
        form = RegistrationForm(request.POST, request.FILES)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password'])
            user.save()
            return redirect('login')
        else:
            print(form.errors)
    return render(request,'register.html',{'form':form})
        



def login(request):
    if request.method == "POST":
        login_input = request.POST['username']
        login_password = request.POST['password']

        try:
            user = User.objects.get(Q(username=login_input) | Q(email=login_input))

            if user.check_password(login_password):
                auth_login(request, user)
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
    auth_logout(request)
    return redirect('login')



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
                user.set_password(new_password)
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
    posts = Post.objects.all().order_by('-created_at')[:6] 
    hero_posts = Post.objects.all().order_by('-created_at')[:3]
    categories = Category.objects.all()
    return render(request, 'index.html', {
        'posts': posts,
        'categories': categories,
        'hero_posts':hero_posts,
    })


def category(request):
    categories = Category.objects.all()
    return render(request,'category.html',{
        'categories':categories
    })


def explore(request):
    categories = Category.objects.all()
    posts = Post.objects.all()
    return render(request,'explore.html',{
        'posts':posts,
        'categories':categories,
    })

def blog_details(request,pk):
    post = Post.objects.get(id=pk)
    comments = Comment.objects.filter(post=post)
    likes = Like.objects.filter(post=post).count()
    is_liked = False

    if request.user.is_authenticated:
        is_liked = Like.objects.filter(
            post=post,
            user = request.user,  
         ).exists()
    
    if request.method == "POST":
        comment_text = request.POST.get('comment')
        if comment_text:
            Comment.objects.create(
                    post=post,
                    user = request.user,
                    comment = comment_text
            )
        return redirect('blog_details',pk=pk)
    

    return render(request,'blog_details.html',{
        'post':post,
        'comments':comments,
        'likes':likes,
        'is_liked':is_liked
    })


@login_required
def like_post(request,pk):
    post = Post.objects.get(id=pk)
    like = Like.objects.filter(post=post, user=request.user)

    if like.exists():
        like.delete()
    else:
        Like.objects.create(post=post,user = request.user)
    return redirect('blog_details', pk=pk)




@login_required
def dashboard(request):
    posts = Post.objects.filter(author=request.user)
    return render (request, 'dashboard.html', {
        'posts':posts
    })

@login_required
def create_post(request):
    form = PostForm()
    categories = Category.objects.all()
    if request.method == "POST":
        form = PostForm(request.POST, request.FILES)
        if form.is_valid():
            post =  form.save(commit=False)
            post.author = request.user
            post.save()
            return redirect('dashboard')
    return render(request, 'create_post.html', {'form': form, 'categories': categories})

@login_required
def edit_post(request,pk):
    post =  Post.objects.get(id=pk)
    form = PostForm(instance=post)
    categories = Category.objects.all()
    if request.method == "POST":
        form = PostForm(request.POST, request.FILES, instance=post)
        if form.is_valid():
            form.save()
            return redirect('dashboard')
        
    return render(request,'edit_post.html',{
        'form':form,
        'categories':categories,
        'post':post
    })

@login_required
def delete_post(request,pk):
    post = Post.objects.get(id=pk)
    post.delete()
    return redirect('dashboard')

@login_required
def profile(request):
     user = request.user
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
            user.profile_photo = request.FILES.get('profile_photo')

        user.save()
        return redirect('profile')
     
     return render(request, 'profile.html',{
         'user':user
     })


def edit_profile(request):
    return render(request, 'edit_profile.html')


def author_story(request):
    return render(request, 'author_story.html')


def author(request):
    return render(request,'author.html')