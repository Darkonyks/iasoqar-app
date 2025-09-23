from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.urls import reverse
from .models import Company, KontaktOsoba
from .contact_forms import KontaktOsobaForm

def kontakt_osoba_create(request, company_id):
    """
    View za kreiranje nove kontakt osobe za kompaniju
    """
    company = get_object_or_404(Company, pk=company_id)
    
    if request.method == 'POST':
        # Direktno koristimo podatke iz POST zahteva
        ime_prezime = request.POST.get('ime_prezime')
        pozicija = request.POST.get('pozicija')
        email = request.POST.get('email')
        telefon = request.POST.get('telefon')
        is_primary = request.POST.get('is_primary') == 'on'
        
        # Validacija
        if not ime_prezime:
            messages.error(request, "Ime i prezime je obavezno polje.")
            return redirect('company:update', pk=company_id)
        
        # Kreiranje kontakt osobe
        kontakt = KontaktOsoba(
            company=company,
            ime_prezime=ime_prezime,
            pozicija=pozicija,
            email=email,
            telefon=telefon,
            is_primary=is_primary
        )
        
        try:
            kontakt.save()
            messages.success(request, f"Kontakt osoba {ime_prezime} je uspešno dodata.")
        except Exception as e:
            messages.error(request, f"Greška prilikom dodavanja kontakt osobe: {str(e)}")
            
        return redirect('company:update', pk=company_id)
    
    # GET zahtev - vraćamo na stranicu za ažuriranje kompanije
    return redirect('company:update', pk=company_id)

def kontakt_osoba_update(request, company_id, pk):
    """
    View za ažuriranje postojeće kontakt osobe
    """
    company = get_object_or_404(Company, pk=company_id)
    kontakt = get_object_or_404(KontaktOsoba, pk=pk, company=company)
    
    if request.method == 'POST':
        form = KontaktOsobaForm(request.POST, instance=kontakt, company=company)
        if form.is_valid():
            form.save()
            messages.success(request, f"Kontakt osoba {kontakt.ime_prezime} je uspešno ažurirana.")
            return redirect('company:update', pk=company_id)
    else:
        form = KontaktOsobaForm(instance=kontakt, company=company)
    
    context = {
        'form': form,
        'company': company,
        'kontakt': kontakt,
        'title': f'Izmena kontakt osobe: {kontakt.ime_prezime}',
        'submit_text': 'Sačuvaj izmene'
    }
    
    return render(request, 'contact/kontakt-form.html', context)

def kontakt_osoba_delete(request, company_id, pk):
    """
    View za brisanje kontakt osobe
    """
    company = get_object_or_404(Company, pk=company_id)
    kontakt = get_object_or_404(KontaktOsoba, pk=pk, company=company)
    
    if request.method == 'POST':
        ime_prezime = kontakt.ime_prezime
        kontakt.delete()
        messages.success(request, f"Kontakt osoba {ime_prezime} je uspešno obrisana.")
        return redirect('company:update', pk=company_id)
    
    context = {
        'company': company,
        'kontakt': kontakt,
    }
    
    return render(request, 'contact/kontakt-confirm-delete.html', context)
