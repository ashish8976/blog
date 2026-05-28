from django import forms
from .models import *

class RegistrationForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput())
    cpassword = forms.CharField(widget=forms.PasswordInput())

    class Meta:
        model = User
        fields = ['fname', 'lname', 'username', 'email', 'profile_photo', 'role']

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        cpassword = cleaned_data.get('cpassword')
        if password != cpassword:
            raise forms.ValidationError("Password and Confirm Password do not match")
        return cleaned_data

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("Email Already Exists")
        return email

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError("Username Already Exists")
        return username
    


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ['post_title','post_desc','post_category','tags','post_image']

    def clean_post_title(self):
        post_title = self.cleaned_data.get('post_title')
        if not post_title:
            raise forms.ValidationError("Enter your Post Title")
        return post_title
        
    def clean_post_desc(self):
        post_desc = self.cleaned_data.get('post_desc')
        if not post_desc or post_desc.strip() == '' or post_desc == '<br>':
             raise forms.ValidationError('Post description not Empty ')
        return post_desc
    
    def clean_post_category(self):
        post_category = self.cleaned_data.get('post_category')
        if not post_category:
            raise forms.ValidationError("Select Your Post Category")
        return post_category
    
    def clean_tags(self):
        tags = self.cleaned_data.get('tags')
        if not tags:
            raise forms.ValidationError("Enter The Tage")
        return tags
        
    