from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import PasswordChangeForm
from .models import UserProfile


class UserForm(forms.ModelForm):
    """Forma za osnovne podatke korisnika"""
    
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email']
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
        }
        labels = {
            'first_name': 'Ime',
            'last_name': 'Prezime',
            'email': 'Email',
        }


class UserProfileForm(forms.ModelForm):
    """Forma za dodatne podatke profila"""
    
    class Meta:
        model = UserProfile
        fields = [
            'phone', 'mobile', 'address', 'city', 'postal_code',
            'business_number', 'department', 'position', 'notes'
        ]
        widgets = {
            'phone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'npr. +381 11 123 4567'}),
            'mobile': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'npr. +381 60 123 4567'}),
            'address': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ulica i broj'}),
            'city': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Grad'}),
            'postal_code': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Poštanski broj'}),
            'business_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Interni poslovni broj'}),
            'department': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Odeljenje'}),
            'position': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Pozicija u firmi'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Dodatne napomene...'}),
        }


class CustomPasswordChangeForm(PasswordChangeForm):
    """Prilagođena forma za promenu lozinke"""
    
    old_password = forms.CharField(
        label='Trenutna lozinka',
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'autocomplete': 'current-password'})
    )
    new_password1 = forms.CharField(
        label='Nova lozinka',
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'autocomplete': 'new-password'})
    )
    new_password2 = forms.CharField(
        label='Potvrda nove lozinke',
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'autocomplete': 'new-password'})
    )
