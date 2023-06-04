from django import forms
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from .models import Profile, Question, Tag, Answer
from django.contrib.auth.models import User
from django.contrib.auth import hashers


class LoginForm(forms.Form):
    username = forms.CharField(widget=forms.TimeInput(
        attrs={
            "class": "login",
            "placeholder": "Enter username"}),
            label="Username"
    )
    password = forms.CharField(widget=forms.PasswordInput(
        attrs={
            "class": "password",
            "placeholder": "Enter password"}),
        label="Password"
    )

    def clean_username(self):
        super().clean()
        username = self.cleaned_data['username']
        if not Profile.objects.get_user_by_username(username):
            self.add_error(field=None, error="Wrong username or password")
        return username

    def clean(self):
        super().clean()
        password = self.cleaned_data['password']
        username = self.cleaned_data['username']
        user = Profile.objects.get_user_by_username(username)
        if not user.check_password(password):
            self.add_error(field=None, error="Wrong username or password")
        return self.cleaned_data


class RegistrationForm(forms.ModelForm):
    password_check = forms.CharField(widget=forms.PasswordInput)
    password = forms.CharField(widget=forms.PasswordInput)
    avatar = forms.ImageField(required=False)
    email = forms.EmailField(required=True)
    username = forms.CharField(required=True)
    nickname = forms.CharField(required=False, widget=forms.TimeInput(
        attrs={
            "class": "nickname"}),
            label="Nickname"
    )

    class Meta:
        model = User
        fields = ['username', 'email', 'nickname', 'password', 'password_check', 'avatar']

    def clean_username(self):
        super().clean()
        username = self.cleaned_data.get('username')

        if Profile.objects.get_user_by_username(username):
            self.add_error('username', IntegrityError("User already exists"))
        return username

    def clean_email(self):
        super().clean()
        email = self.cleaned_data.get('email')
        if Profile.objects.get_user_by_email(email):
            self.add_error('email', IntegrityError("User already exists"))
        return email

    def clean(self):
        super().clean()
        pas1 = self.cleaned_data.get("password")
        pas2 = self.cleaned_data.get("password_check")
        if pas1 and pas1 != pas2:
            self.add_error('password_check', ValidationError("Passwords don't match", code='invalid'))
        return self.cleaned_data

    def save(self):
        self.cleaned_data.pop('password_check')
        nickname = self.cleaned_data.pop('nickname')
        avatar = self.files.get('avatar')
        self.cleaned_data.pop('avatar')
        user = User.objects.create_user(**self.cleaned_data)
        profile = Profile.objects.create(user=user, nickname=nickname)
        if avatar:
            profile.avatar = avatar
        profile.save()
        return profile


class SettingsForm(forms.ModelForm):
    username = forms.CharField(disabled=True)
    email = forms.CharField(disabled=True)
    old_password = forms.CharField(widget=forms.PasswordInput, required=False)
    password_check = forms.CharField(widget=forms.PasswordInput, required=False)
    new_password = forms.CharField(widget=forms.PasswordInput, required=False)
    avatar = forms.FileField(widget=forms.FileInput(attrs={
        "class": "form-control"}),
        label="Avatar",
        required=False)
    nickname = forms.CharField()

    class Meta:
        model = User
        fields = ['username', 'email', 'nickname', 'old_password', 'password_check', 'new_password', 'avatar']

    def clean_old_password(self):
        super().clean()
        password = self.cleaned_data['old_password']
        user = self.instance
        if not password:
            return password
        if not user.check_password(password):
            self.add_error('old_password', error="Wrong password")
        return password

    def clean(self):
        super().clean()
        pas1 = self.cleaned_data.get("old_password")
        pas2 = self.cleaned_data.get("password_check")
        pas3 = self.cleaned_data.get("new_password")

        if pas1 and pas1 != pas2:
            self.add_error('password_check', ValidationError("Passwords don't match", code='invalid'))

        if pas1 and pas3 and pas1 == pas3:
            self.add_error('new_password', ValidationError("Password doesn't change", code='invalid'))

        return self.cleaned_data

    def save(self):
        pas3 = self.cleaned_data.get("new_password")
        nickname = self.cleaned_data.get('nickname')
        user = super().save()
        if pas3:
            user.password = hashers.make_password(pas3)
        avatar = self.files.get('avatar')

        profile = user.profile
        if avatar:
            profile.avatar = avatar
        profile.nickname = nickname
        profile.save()
        user.save()


class QuestionForm(forms.ModelForm):
    title = forms.CharField(required=True)
    description = forms.CharField(widget=forms.Textarea(attrs={"rows" : "5"}))
    tags = forms.CharField()

    class Meta:
        model = Question
        fields = ['title', 'description', 'tags']

    def save(self, profile):
        super().clean()
        question = Question.objects.create(
            title=self.cleaned_data['title'],
            description=self.cleaned_data['description'],
            author=profile
        )
        tag_names = self.cleaned_data['tags'].split(',')
        tags = []
        for tag_name in tag_names:
            tag, created = Tag.objects.get_or_create(title=tag_name)
            tags.append(tag)
        for tag in tags:
            question.tags.add(tag)
        return question.id


class AnswerForm(forms.Form):
    description = forms.CharField(widget=forms.Textarea(attrs={"rows": "5"}))

    def save(self, profile, question):
        super().clean()
        answer = Answer.objects.create(
            description=self.cleaned_data['description'],
            author=profile,
            question=question
        )
        return answer.id
