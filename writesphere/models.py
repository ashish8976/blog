from django.db import models

# Create your models here.


class User(models.Model):
    fname = models.CharField(max_length=50)
    lname = models.CharField(max_length=50)
    username = models.CharField(max_length=150, unique=True)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=255)
    role = models.CharField(max_length=50, default="Reader") 
    profile_photo = models.ImageField(upload_to='profile_photos/', null=True, blank=True)
    bio = models.TextField(null=True, blank=True)

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
