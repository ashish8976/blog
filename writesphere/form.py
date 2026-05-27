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