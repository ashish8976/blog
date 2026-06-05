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
from django.db.models import Count
from django.utils import timezone
from datetime import timedelta
import json
from django.contrib.auth import update_session_auth_hash
from django.contrib import messages
from dateutil.relativedelta import relativedelta



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


@login_required
def update_password(request):
    pw_error = None
    pw_success = None

    if request.method == 'POST':
        current = request.POST.get('current_password')
        new = request.POST.get('new_password')
        confirm = request.POST.get('confirm_password')

        if not request.user.check_password(current):
            pw_error = {'field': 'current', 'msg': 'Current password is incorrect.'}
        elif new != confirm:
            pw_error = {'field': 'confirm', 'msg': 'Passwords do not match.'}
        elif len(new) < 6:
            pw_error = {'field': 'new', 'msg': 'Password must be at least 6 characters.'}
        else:
            request.user.set_password(new)
            request.user.save()
            update_session_auth_hash(request, request.user)
            pw_success = True

    return redirect('dashboard')


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
            entered_otp = request.POST.get('uotp')
            session_otp = request.session.get('otp')
            otp_time = request.session.get('otp_time')

            if time.time() - otp_time > 300:  
                msg = "OTP expired. Try again."
                return render(request, 'otp.html', {'msg': msg})

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
    return render(request, 'category.html', {'categories': categories})

def category_posts(request, cat_id):
    cat = Category.objects.get(id=cat_id)
    posts = Post.objects.filter(post_category=cat)
    return render(request, 'category_posts.html', {'cat': cat, 'posts': posts})


def explore(request):
    categories = Category.objects.all()
    posts = Post.objects.all()
    query = request.GET.get('q' , '')
    category_filter = request.GET.get('category','')

    if query:
        posts = posts.filter(
            Q(post_title__icontains=query) |
            Q(author__fname__icontains=query) |     
            Q(author__lname__icontains=query) |      
            Q(author__username__icontains=query) |   
            Q(tags__icontains=query) |
            Q(post_category__name__icontains=query)  
        )
    if category_filter:
        posts = posts.filter(post_category = category_filter)


    return render(request,'explore.html',{
        'posts':posts,
        'categories':categories,
        'query': query,
        'category_filter':category_filter
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
    pw_error = None
    pw_success = False

    if request.method == 'POST':
        current = request.POST.get('current_password')
        new = request.POST.get('new_password')
        confirm = request.POST.get('confirm_password')

        if not request.user.check_password(current):
            pw_error = {'field': 'current', 'msg': 'Current password is incorrect.'}
        elif new != confirm:
            pw_error = {'field': 'confirm', 'msg': 'Passwords do not match.'}
        elif len(new) < 6:
            pw_error = {'field': 'new', 'msg': 'Password must be at least 6 characters.'}
        else:
            request.user.set_password(new)
            request.user.save()
            update_session_auth_hash(request, request.user)
            pw_success = True

    posts = Post.objects.filter(author=request.user)
    total_likes = sum(post.likes.count() for post in posts)
    total_comments = sum(post.comments.count() for post in posts)

    monthly_posts = []
    monthly_labels = []
    for i in range(5, -1, -1):
        date = timezone.now() - relativedelta(months=i)
        counts = posts.filter(created_at__year=date.year, created_at__month=date.month).count()
        monthly_posts.append(counts)
        monthly_labels.append(date.strftime('%b %Y'))

    weekly_posts = []
    weekly_labels = []
    for i in range(6, -1, -1):
        date = timezone.now() - timedelta(days=i)
        counts = posts.filter(created_at__date=date.date()).count()
        weekly_posts.append(counts)
        weekly_labels.append(date.strftime('%a'))

    top_posts = []
    top_likes = []
    top_comments = []
    for post in posts.order_by('-created_at')[:5]:
        top_posts.append(post.post_title[:20] + '...' if len(post.post_title) > 20 else post.post_title)
        top_likes.append(post.likes.count())
        top_comments.append(post.comments.count())

    return render(request, 'dashboard.html', {
        'posts': posts,
        'total_likes': total_likes,
        'total_comments': total_comments,
        'monthly_labels': json.dumps(monthly_labels),
        'monthly_posts': json.dumps(monthly_posts),
        'weekly_labels': json.dumps(weekly_labels),
        'weekly_posts': json.dumps(weekly_posts),
        'top_posts': json.dumps(top_posts),
        'top_likes': json.dumps(top_likes),
        'top_comments': json.dumps(top_comments),
        'pw_error': pw_error,
        'pw_success': pw_success,
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
    if post.author != request.user:  
        return redirect('dashboard')
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
    if post.author != request.user:  
        return redirect('dashboard')
    post.delete()
    return redirect('dashboard')


@login_required
def profile(request):
    user = request.user
    if request.method == "POST":
         if request.FILES.get('profile_photo'):
             user.profile_photo = request.FILES.get('profile_photo')
             user.save()
             request.session['user_image'] = user.profile_photo.url
             return redirect('profile')


         user.fname = request.POST.get('fname', user.fname)
         user.lname = request.POST.get('lname', user.lname)
         user.email = request.POST.get('email', user.email)
         user.username = request.POST.get('username', user.username)
         user.bio = request.POST.get('bio',user.bio)
         user.save()
         return redirect('profile')
         
    return render(request,'profile.html',{
        'user':user
    })


@login_required
def follow_user(request, pk):
    user_to_follow = User.objects.get(id=pk)
    follow = Follow.objects.filter(follower=request.user, following=user_to_follow)
    
    if follow.exists():
        follow.delete()  
    else:
        Follow.objects.create(follower=request.user, following=user_to_follow)  # Follow karo
    
    return redirect(request.META.get('HTTP_REFERER', 'index'))


def author_story(request):
    return render(request, 'author_story.html')


@login_required
def author_detail(request, pk):
    author = User.objects.get(id=pk)
    posts = Post.objects.filter(author=author)
    is_following = False
    followers_count = Follow.objects.filter(following=author).count()
    following_count = Follow.objects.filter(follower=author).count()

    if request.user.is_authenticated:
        is_following = Follow.objects.filter(
            follower=request.user,
            following=author
        ).exists()

    return render(request, 'author_detail.html', {
        'author': author,
        'posts': posts,
        'is_following': is_following,
        'followers_count': followers_count,
        'following_count': following_count,
    })

@login_required
def author(request):
    authors = User.objects.filter(role='Author')
    
    following_ids = []
    if request.user.is_authenticated:
        following_ids = Follow.objects.filter(
            follower=request.user
        ).values_list('following_id', flat=True)

    total_posts = Post.objects.filter(author__in=authors).count() 
    
    return render(request, 'author.html', {
        'authors': authors,
        'following_ids': following_ids,
        'total_posts' : total_posts,
    })


