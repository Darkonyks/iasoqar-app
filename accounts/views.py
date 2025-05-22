from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.contrib import messages


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
    return render(request, 'accounts/profile.html', {'user': request.user})
