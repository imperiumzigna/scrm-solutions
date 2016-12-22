from django import forms
from django.contrib.auth.models import User

from .models import Workspace, Fanpage, Post, Tagged, Tweet, Contact


class UserForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ['username', 'email', 'password']

class WorkspaceFacebookForm(forms.ModelForm):

    class Meta:
        model = Workspace
        fields = ['extracao_facebook', 'user_token']

class WorkspaceTwitterForm(forms.ModelForm):

    class Meta:
        model = Workspace
        fields = ['extracao_twitter', 'ckey', 'csecret', 'atoken', 'asecret']


class FacebookFanpageForm(forms.ModelForm):

    class Meta:
        model = Fanpage
        fields = ['page']

class FacebookPostForm(forms.ModelForm):

    class Meta:
        model = Post
        fields = ['tipo_extracao']

class FacebookTaggedForm(forms.ModelForm):

    class Meta:
        model = Tagged
        fields = ['page', 'tipo_extracao']

# Forms para tweeter

class TwitterPostForm(forms.ModelForm):
    class Meta:
        model = Tweet
        fields = ['termo_consulta']
        
# Fim Forms para tweeter


class ContactForm(forms.ModelForm):
    
    class Meta:
        model = Contact
        fields = ['name', 'email', 'message', 'phone']
