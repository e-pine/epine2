from django.forms import ModelForm
from django.contrib.auth.forms import UserCreationForm
from django import forms
from django.contrib.auth.models import User, Group
from .models import *
from django.contrib.auth.forms import PasswordResetForm, SetPasswordForm

class CreateUserForm(UserCreationForm):

    # ROLES = (
    #     ('','Select a role'),
    #     ('buyer', 'Buyer'),
    #     ('employee', 'Employee'),
    # )
    # role = forms.ChoiceField(choices=ROLES)

    class Meta:
        model = User 
        # fields = ['username', 'email', 'first_name', 'last_name', 'role', 'password1', 'password2']
        fields = ['username', 'email', 'first_name', 'last_name', 'password1', 'password2']

    def save(self, commit=True):
        user = super().save(commit=False)
        if commit:
            user.save()
            # role = self.cleaned_data.get('role')
            role = 'buyer'
            try:
                group = Group.objects.get(name=role)
                user.groups.add(group)
            except Group.DoesNotExist:
                user.delete()
                raise forms.ValidationError('Invalid role. Please select a valid role.')

        return user

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Username'})
        self.fields['email'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Email'})
        self.fields['first_name'].widget.attrs.update({'class': 'form-control', 'placeholder': 'First name'})
        self.fields['last_name'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Last name'})
        # self.fields['phone_number'].widget.attrs.update({'class': 'form-control', 'placeholder': 'your number'})
        self.fields['password1'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Password'})
        self.fields['password2'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Re-type password'})
        # self.fields['role'].widget.attrs.update({'class': 'form-control'})

        self.fields['username'].error_messages['unique'] = 'This username is already taken. Please choose a different one.'


class AddUserForm(UserCreationForm):

    ROLES = (
        ('','Select a role'),
        ('buyer', 'Buyer'),
        ('employee', 'Employee'),
    )
    role = forms.ChoiceField(choices=ROLES)

    class Meta:
        model = User 
        fields = ['username', 'email', 'first_name', 'last_name', 'role', 'password1', 'password2']

    def save(self, commit=True):
        user = super().save(commit=False)
        if commit:
            user.save()
            role = self.cleaned_data.get('role')
        
            try:
                group = Group.objects.get(name=role)
                user.groups.add(group)
            except Group.DoesNotExist:
                user.delete()
                raise forms.ValidationError('Invalid role. Please select a valid role.')

        return user

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Username'})
        self.fields['email'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Email'})
        self.fields['first_name'].widget.attrs.update({'class': 'form-control', 'placeholder': 'First name'})
        self.fields['last_name'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Last name'})
        # self.fields['phone_number'].widget.attrs.update({'class': 'form-control', 'placeholder': 'your number'})
        self.fields['password1'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Password'})
        self.fields['password2'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Re-type password'})
        self.fields['role'].widget.attrs.update({'class': 'form-control'})

        self.fields['username'].error_messages['unique'] = 'This username is already taken. Please choose a different one.'

class CustomPasswordResetForm(PasswordResetForm):
    email = forms.EmailField(
        label='Email',
        max_length=254,
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Email Account'}),
    )

    def clean_email(self):
        email = self.cleaned_data['email']
        # Add custom validation if needed
        return email
    
class CustomSetPasswordForm(SetPasswordForm):
    new_password1 = forms.CharField(
        label='New Password',
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'New Password'}),
    )
    new_password2 = forms.CharField(
        label='Confirm New Password',
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Confirm New Password'}),
    )