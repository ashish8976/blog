from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin


class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('Email required')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user
    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(email, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    fname = models.CharField(max_length=50)
    lname = models.CharField(max_length=50)
    username = models.CharField(max_length=150, unique=True)
    email = models.EmailField(unique=True)
    role = models.CharField(max_length=50, default="Reader")
    profile_photo = models.ImageField(upload_to='profile_photos/', null=True, blank=True)
    bio = models.TextField(null=True, blank=True)
    is_active = models.BooleanField(default=True)  
    is_staff = models.BooleanField(default=False) 

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']
    objects = UserManager()

    def __str__(self):
        return f"{self.fname} {self.lname}"


class Post(models.Model):
    CATEGORY_CHOICES = (
        ('Technology', 'Technology'),
        ('Travel', 'Travel'),
        ('Wellness', 'Wellness'),
        ('Design', 'Design'),
        ('Science', 'Science'),
        ('Fiction', 'Fiction'),
        ('Philosophy', 'Philosophy'),
        ('Culture', 'Culture'),
    )

    post_title = models.CharField(max_length=200)
    post_desc = models.TextField()
    post_image = models.ImageField(upload_to='post_images/', blank=True, null=True)
    post_category = models.CharField(max_length=100, choices=CATEGORY_CHOICES)
    tags = models.CharField(max_length=300, blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.post_title
