from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout, update_session_auth_hash
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from .forms import UserForm, UserProfileForm, CustomPasswordChangeForm
from .models import UserProfile


def login_view(request):
    """
    Pogled za prijavu korisnika.
    """
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                next_url = request.GET.get('next', 'company:dashboard')
                return redirect(next_url)
            else:
                messages.error(request, 'Neispravno korisničko ime ili lozinka.')
        else:
            messages.error(request, 'Neispravno korisničko ime ili lozinka.')
    else:
        form = AuthenticationForm()
    
    return render(request, 'accounts/login.html', {'form': form})


def register_view(request):
    """
    Pogled za registraciju novog korisnika.
    """
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Registracija uspešna! Dobrodošli!')
            return redirect('company:dashboard')
    else:
        form = UserCreationForm()
    
    return render(request, 'accounts/register.html', {'form': form})


def logout_view(request):
    """
    Pogled za odjavu korisnika.
    """
    logout(request)
    messages.info(request, 'Uspešno ste se odjavili.')
    return redirect('accounts:login')


@login_required
def profile_view(request):
    """
    Pogled za prikaz i ažuriranje korisničkog profila.
    """
    # Osiguraj da korisnik ima profil
    profile, created = UserProfile.objects.get_or_create(user=request.user)
    
    if request.method == 'POST':
        action = request.POST.get('action', 'update_profile')
        print(f"DEBUG: action={action}, POST data keys: {list(request.POST.keys())}")
        
        if action == 'update_profile':
            user_form = UserForm(request.POST, instance=request.user)
            profile_form = UserProfileForm(request.POST, instance=profile)
            
            if user_form.is_valid() and profile_form.is_valid():
                user_form.save()
                profile_form.save()
                messages.success(request, 'Profil je uspešno ažuriran.')
                return redirect('accounts:profile')
            else:
                messages.error(request, 'Molimo ispravite greške u formi.')
                password_form = CustomPasswordChangeForm(request.user)
        
        elif action == 'change_password':
            password_form = CustomPasswordChangeForm(request.user, request.POST)
            print(f"DEBUG password_form.data: {dict(request.POST)}")
            print(f"DEBUG password_form.is_valid(): {password_form.is_valid()}")
            print(f"DEBUG password_form.errors: {password_form.errors}")
            
            if password_form.is_valid():
                user = password_form.save()
                # Održi korisnika ulogovanog nakon promene lozinke
                update_session_auth_hash(request, user)
                messages.success(request, 'Lozinka je uspešno promenjena.')
                return redirect('accounts:profile')
            else:
                # Prikaži sve greške
                for field, errors in password_form.errors.items():
                    for error in errors:
                        messages.error(request, f'{error}')
                user_form = UserForm(instance=request.user)
                profile_form = UserProfileForm(instance=profile)
    else:
        user_form = UserForm(instance=request.user)
        profile_form = UserProfileForm(instance=profile)
        password_form = CustomPasswordChangeForm(request.user)
    
    context = {
        'user': request.user,
        'user_form': user_form,
        'profile_form': profile_form,
        'password_form': password_form,
    }
    
    return render(request, 'accounts/profile.html', context)
