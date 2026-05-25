"""
URL configuration for blogproject project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.contrib import admin
from django.urls import path
from writesphere import views


urlpatterns = [
    path('index/', views.index, name="index"),
    path('explore/',views.explore,name="explore"),
    path('blog_detail/',views.blog_details,name="blog_detail"),
    path('dashboard/',views.dashboard,name="dashboard"),
    path('login/',views.login,name="login"),
    path('register/',views.register,name="register"),
    path('author/',views.author,name="author"),
    path('logout/',views.logout,name='logout'),
    path('otp/',views.otp,name='otp'),
    path('forgetpassword/',views.forgetpassword,name='forgetpassword'),
    path('resetpassword/',views.resetpassword,name='resetpassword'),
    path('create_post/',views.create_post,name='create_post'),
    path('author_story/',views.author_story,name='author_story'),
    path('profile/', views.profile, name="profile"),
    path('edit_profile/', views.edit_profile, name="edit_profile"),
    path('category/',views.category,name='category')

]
