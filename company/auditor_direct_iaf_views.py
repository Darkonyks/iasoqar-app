from django.shortcuts import get_object_or_404, redirect, render
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import connection
from django.utils import timezone
from django.urls import reverse

from .auditor_models import Auditor, AuditorIAFEACCode
from .auditor_direct_iaf_form import DirectIAFEACCodeForm


@login_required
def auditor_direct_iaf_eac_create(request, auditor_id):
    """View za direktno dodavanje IAF/EAC koda tehničkom ekspertu"""
    auditor = get_object_or_404(Auditor, pk=auditor_id)
    
    # Proveri da li je auditor tehnički ekspert
    if auditor.kategorija != Auditor.CATEGORY_TECHNICAL_EXPERT:
        messages.error(request, 'IAF/EAC kodovi se mogu direktno dodavati samo tehničkim ekspertima.')
        return redirect('company:auditor_detail', pk=auditor.id)
    
    if request.method == 'POST':
        # Koristimo novu formu koja ne koristi Django ORM
        form = DirectIAFEACCodeForm(request.POST)
        if form.is_valid():
            # Uzimamo vrednosti iz forme
            iaf_eac_code = form.cleaned_data['iaf_eac_code']
            is_primary = form.cleaned_data['is_primary']
            notes = form.cleaned_data['notes']
            
            # Provera da li već postoji veza sa ovim IAF/EAC kodom - direktan SQL upit
            with connection.cursor() as cursor:
                # Provera da li već postoji veza
                cursor.execute(
                    "SELECT COUNT(*) FROM company_auditoriafeaccode WHERE auditor_id = %s AND iaf_eac_code_id = %s",
                    [auditor.id, iaf_eac_code.id]
                )
                count = cursor.fetchone()[0]
                
                if count > 0:
                    messages.error(request, f'Auditor već ima dodeljen IAF/EAC kod {iaf_eac_code}.')
                    return redirect('company:auditor_detail', pk=auditor.id)
                
                # Ako je označen kao primarni, poništi sve druge primarne kodove za ovog auditora
                if is_primary:
                    cursor.execute(
                        "UPDATE company_auditoriafeaccode SET is_primary = %s WHERE auditor_id = %s",
                        [False, auditor.id]
                    )
                
                # Dodaj novi IAF/EAC kod - direktan SQL upit bez korišćenja ORM-a
                cursor.execute(
                    """INSERT INTO company_auditoriafeaccode 
                       (auditor_id, iaf_eac_code_id, is_primary, notes) 
                       VALUES (%s, %s, %s, %s)""",
                    [auditor.id, iaf_eac_code.id, is_primary, notes or '']
                )
            
            messages.success(request, f'IAF/EAC kod {iaf_eac_code} je uspešno dodeljen tehničkom ekspertu {auditor.ime_prezime}.')
            return redirect('company:auditor_detail', pk=auditor.id)
    else:
        form = DirectIAFEACCodeForm()
    
    context = {
        'title': f'Dodavanje IAF/EAC koda za tehničkog eksperta: {auditor.ime_prezime}',
        'form': form,
        'auditor': auditor,
        'submit_text': 'Sačuvaj'
    }
    
    return render(request, 'auditor/auditor_direct_iaf_eac_form.html', context)


@login_required
def auditor_direct_iaf_eac_update(request, auditor_id, pk):
    """View za izmenu direktno dodeljenog IAF/EAC koda tehničkom ekspertu"""
    auditor = get_object_or_404(Auditor, pk=auditor_id)
    
    # Dohvatamo podatke o IAF/EAC kodu direktno iz baze
    with connection.cursor() as cursor:
        cursor.execute(
            """SELECT c.id, c.iaf_code, c.description, a.is_primary, a.notes 
               FROM company_auditoriafeaccode a 
               JOIN company_iafeaccode c ON a.iaf_eac_code_id = c.id 
               WHERE a.id = %s AND a.auditor_id = %s""",
            [pk, auditor_id]
        )
        row = cursor.fetchone()
        
        if not row:
            messages.error(request, 'Traženi IAF/EAC kod nije pronađen.')
            return redirect('company:auditor_detail', pk=auditor.id)
        
        iaf_eac_id, iaf_code, description, is_primary, notes = row
        current_iaf_eac_code = f"{iaf_code} - {description}"
    
    if request.method == 'POST':
        # Ne koristimo formu za validaciju - direktno čitamo iz POST podataka
        # Jedina polja koja dozvoljavamo da se menjaju su is_primary i notes
        is_primary = 'is_primary' in request.POST
        notes = request.POST.get('notes', '')
        
        # Ako je označen kao primarni, poništi sve druge primarne kodove za ovog auditora
        if is_primary:
            with connection.cursor() as cursor:
                cursor.execute(
                    "UPDATE company_auditoriafeaccode SET is_primary = %s WHERE auditor_id = %s AND id != %s",
                    [False, auditor.id, pk]
                )
        
        # Ažuriraj samo is_primary i notes za IAF/EAC kod
        with connection.cursor() as cursor:
            cursor.execute(
                "UPDATE company_auditoriafeaccode SET is_primary = %s, notes = %s WHERE id = %s",
                [is_primary, notes, pk]
            )
        
        messages.success(request, f'IAF/EAC kod {current_iaf_eac_code} je uspešno ažuriran.')
        return redirect('company:auditor_detail', pk=auditor.id)
    else:
        # Za GET zahtev, pripremamo podatke za prikaz u formi
        form_data = {
            'iaf_eac_code': current_iaf_eac_code,
            'is_primary': is_primary,
            'notes': notes
        }
    
    context = {
        'title': f'Izmena IAF/EAC koda za tehničkog eksperta: {auditor.ime_prezime}',
        'auditor': auditor,
        'iaf_eac_id': pk,
        'iaf_code': iaf_code,
        'description': description,
        'is_primary': is_primary,
        'notes': notes,
        'current_iaf_eac_code': current_iaf_eac_code,
        'submit_text': 'Sačuvaj'
    }
    
    return render(request, 'auditor/auditor_direct_iaf_eac_manual_edit.html', context)


@login_required
def auditor_direct_iaf_eac_delete(request, auditor_id, pk):
    """View za brisanje direktno dodeljenog IAF/EAC koda tehničkom ekspertu"""
    auditor = get_object_or_404(Auditor, pk=auditor_id)
    
    # Dohvatamo podatke o IAF/EAC kodu direktno iz baze
    with connection.cursor() as cursor:
        cursor.execute(
            """SELECT c.id, c.iaf_code, c.description 
               FROM company_auditoriafeaccode a 
               JOIN company_iafeaccode c ON a.iaf_eac_code_id = c.id 
               WHERE a.id = %s AND a.auditor_id = %s""",
            [pk, auditor_id]
        )
        row = cursor.fetchone()
        
        if not row:
            messages.error(request, 'Traženi IAF/EAC kod nije pronađen.')
            return redirect('company:auditor_detail', pk=auditor.id)
        
        iaf_eac_id, iaf_code, description = row
        iaf_eac_code = f"{iaf_code} - {description}"
    
    if request.method == 'POST':
        # Brišemo IAF/EAC kod direktno iz baze
        with connection.cursor() as cursor:
            cursor.execute(
                "DELETE FROM company_auditoriafeaccode WHERE id = %s AND auditor_id = %s",
                [pk, auditor_id]
            )
        
        messages.success(request, f'IAF/EAC kod {iaf_eac_code} je uspešno obrisan.')
        return redirect('company:auditor_detail', pk=auditor.id)
    
    context = {
        'title': 'Brisanje IAF/EAC koda',
        'object_name': iaf_eac_code,
        'object_type': 'IAF/EAC kod',
        'auditor': auditor,
        'cancel_url': reverse('company:auditor_detail', kwargs={'pk': auditor.id})
    }
    
    return render(request, 'auditor/generic_confirm_delete.html', context)
