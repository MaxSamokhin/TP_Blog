from django.http import HttpResponse, Http404
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django import forms

from django.contrib.auth.hashers import make_password
from app.models import Profile, Question, Tag, Answer

import urllib, re
from django.core.files import File
import requests
from django.core.files.base import ContentFile

from django.forms import Field


class LoginForm(forms.Form):
    login = forms.CharField(
        widget=forms.TextInput(
            attrs={'class': 'form-control', 'placeholder': 'login', }
        ),
        max_length=30,
        label='Login'
    )

    password = forms.CharField(
        widget=forms.PasswordInput(
            attrs={'class': 'form-control', 'placeholder': '*******', }
        ),
        label='Password'
    )

    def clean(self):
        data = self.cleaned_data
        user = authenticate(username=data.get('login', ''), password=data.get('password', ''))

        if user is not None:
            if user.is_active:
                data['user'] = user
            else:
                raise forms.ValidationError('This user don\'t active')
        else:
            raise forms.ValidationError('Uncorrect login or password')


class SignupForm(forms.Form):
    username = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'login', }),
        max_length=25,
        label='Login'
    )
    first_name = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'name', }),
        max_length=25,
        label='Name'
    )
    last_name = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'second name', }),
        max_length=25,
        label='Second name'
    )
    email = forms.EmailField(
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'me@gmail.com', }),
        required=False, max_length=254, label='E-mail'
    )
    password1 = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': '*****'}),
        min_length=6,
        label='Password'
    )
    password2 = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': '*****'}),
        min_length=6,
        label='Repeat password'
    )
    avatar = forms.FileField(
        widget=forms.ClearableFileInput(
            attrs={}),
        required=False, label='Avatar'
    )

    # avatar = forms.ImageField(
    #     widget=forms.ClearableFileInput(
    #         attrs={'class': 'ask-signup-avatar-input', }),
    #     required=False, label='Avatar'
    # )

    def clean_username(self):
        username = self.cleaned_data.get('username', '')

        try:
            u = User.objects.get(username=username)
            raise forms.ValidationError('User exist')
        except User.DoesNotExist:
            return username

    def clean_password2(self):
        pass1 = self.cleaned_data.get('password1', '')
        pass2 = self.cleaned_data.get('password2', '')

        if pass1 != pass2:
            raise forms.ValidationError('Passwords not equal')

    def save(self):
        data = self.cleaned_data
        password = data.get('password1')
        u = User()

        u.username = data.get('username')
        u.password = make_password(password)
        u.email = data.get('email')
        u.first_name = data.get('first_name')
        u.last_name = data.get('last_name')
        u.is_active = True
        u.is_superuser = False
        u.save()

        up = Profile()
        up.user = u

        if data.get('avatar') is None:
            # image_url = 'http://api.adorable.io/avatars/100/%s.png' % u.username
            # response = requests.get(image_url)
            #
            # up.avatar.save('%s.png' % u.username, ContentFile(response.content), save=True)
            up.avatar.save('%s.png' % u.username, 'default.jpg', save=True)


        else:
            avatar = data.get('avatar')
            up.avatar.save('%s_%s' % (u.username, avatar.name), avatar, save=True)

        up.save()

        return authenticate(username=u.username, password=password)


class ProfileEditForm(forms.Form):
    first_name = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control',
                                      'placeholder': 'name', }),
        max_length=30, label='Name'
    )
    last_name = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control',
                                      'placeholder': 'last name', }),
        max_length=30, label='First name'
    )
    email = forms.EmailField(
        widget=forms.TextInput(attrs={'class': 'form-control',
                                      'placeholder': 'me@gmail.com', }),
        required=False, max_length=254, label='E-mail'
    )
    password1 = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control',
                                          'placeholder': '*****'}),
        min_length=6, label='Password', required=False
    )
    password2 = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control',
                                          'placeholder': '*****'}),
        min_length=6, label='Repeat password', required=False
    )

    avatar = forms.ImageField(
        widget=forms.ClearableFileInput(
            attrs={'class': 'ask-signup-avatar-input', }),
        required=False, label='Avatar'
    )

    def clean_password2(self):
        pass1 = self.cleaned_data.get('password1', '')
        pass2 = self.cleaned_data.get('password2', '')
        if pass1 != pass2:
            raise forms.ValidationError('Passwords not equal')

    def save(self, user):
        data = self.cleaned_data
        user.first_name = data.get('first_name')
        user.last_name = data.get('last_name')
        user.email = data.get('email')
        pass1 = self.cleaned_data.get('password1', '')
        if pass1 != '':
            user.set_password(pass1)
        user.save()
        up = user.profile

        # add_avatar

        if data.get('avatar') is not None:
            avatar = data.get('avatar')
            up.avatar.save('%s_%s' % (user.username, avatar.name), avatar, save=True)

        up.save()
        return self


class AskForm(forms.Form):
    title = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control form-control-danger'}),
        min_length=3,
        label='Title',
        error_messages={'min_length': 'min length %(limit_value)d', 'required': 'need title!'},
    )
    question = forms.CharField(
        widget=forms.Textarea(attrs={'class': 'form-control form-control-danger'}),
        min_length=3,
        label='Text',
        error_messages={'min_length': 'min length %(limit_value)d', 'required': 'input question!'},
    )
    tags = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        label='Tags',
        required=False
    )

    def save(self, user):
        data = self.cleaned_data
        title = data.get('title', '')
        text = data.get('question', '')
        _tags = data.get('tags', '')

        q = Question()
        q.title = title
        q.text = text
        q.author = user
        q.save()

        if _tags != '':
            tags = re.split('\s+', _tags)
            print(tags)
            for tag in tags:
                print(tag)
                t = Tag.objects.get_or_create(title=tag)[0]
                q.tags.add(t)

        return q


class AnswerForm(forms.Form):
    text = forms.CharField(
        widget=forms.Textarea(attrs={'class': 'form-control',
                                     'rows': '6',
                                     'placeholder': 'Input your answer',
                                     })
    )

    def save(self, question, author):
        data = self.cleaned_data
        return question.answer_set.create(text=data.get('text'), author=author)
