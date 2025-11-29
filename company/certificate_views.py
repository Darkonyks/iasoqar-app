"""
Views za CRUD operacije nad Certificate modelom
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_POST, require_http_methods
from django.urls import reverse

from .models import Company, Certificate


def certificate_create(request, company_id):
    """Kreiranje novog sertifikata za kompaniju"""
    company = get_object_or_404(Company, pk=company_id)
    
    if request.method == 'POST':
        certificate_number = request.POST.get('certificate_number', '').strip()
        status = request.POST.get('status', 'pending')
        issue_date = request.POST.get('issue_date') or None
        expiry_date = request.POST.get('expiry_date') or None
        suspension_until_date = request.POST.get('suspension_until_date') or None
        notes = request.POST.get('notes', '').strip()
        
        if not certificate_number:
            messages.error(request, 'Broj sertifikata je obavezan.')
            return redirect('company:detail', pk=company_id)
        
        # Proveri da li sertifikat sa tim brojem već postoji
        if Certificate.objects.filter(certificate_number=certificate_number).exists():
            messages.error(request, f'Sertifikat sa brojem {certificate_number} već postoji.')
            return redirect('company:detail', pk=company_id)
        
        try:
            certificate = Certificate.objects.create(
                company=company,
                certificate_number=certificate_number,
                status=status,
                issue_date=issue_date,
                expiry_date=expiry_date,
                suspension_until_date=suspension_until_date,
                notes=notes
            )
            messages.success(request, f'Sertifikat {certificate_number} je uspešno kreiran.')
        except Exception as e:
            messages.error(request, f'Greška pri kreiranju sertifikata: {str(e)}')
        
        # Vrati na tab Sertifikati
        return redirect(f"{reverse('company:detail', kwargs={'pk': company_id})}#certificates")
    
    # GET zahtev - prikaži formu
    context = {
        'company': company,
        'title': f'Novi sertifikat za {company.name}',
        'status_choices': Certificate.STATUS_CHOICES,
    }
    return render(request, 'company/certificate-form.html', context)


def certificate_update(request, company_id, pk):
    """Ažuriranje postojećeg sertifikata"""
    company = get_object_or_404(Company, pk=company_id)
    certificate = get_object_or_404(Certificate, pk=pk, company=company)
    
    if request.method == 'POST':
        certificate_number = request.POST.get('certificate_number', '').strip()
        status = request.POST.get('status', 'pending')
        issue_date = request.POST.get('issue_date') or None
        expiry_date = request.POST.get('expiry_date') or None
        suspension_until_date = request.POST.get('suspension_until_date') or None
        notes = request.POST.get('notes', '').strip()
        
        if not certificate_number:
            messages.error(request, 'Broj sertifikata je obavezan.')
            return redirect('company:certificate_update', company_id=company_id, pk=pk)
        
        # Proveri da li sertifikat sa tim brojem već postoji (osim trenutnog)
        if Certificate.objects.filter(certificate_number=certificate_number).exclude(pk=pk).exists():
            messages.error(request, f'Sertifikat sa brojem {certificate_number} već postoji.')
            return redirect('company:certificate_update', company_id=company_id, pk=pk)
        
        try:
            certificate.certificate_number = certificate_number
            certificate.status = status
            certificate.issue_date = issue_date
            certificate.expiry_date = expiry_date
            certificate.suspension_until_date = suspension_until_date
            certificate.notes = notes
            certificate.save()
            messages.success(request, f'Sertifikat {certificate_number} je uspešno ažuriran.')
        except Exception as e:
            messages.error(request, f'Greška pri ažuriranju sertifikata: {str(e)}')
        
        # Vrati na tab Sertifikati
        return redirect(f"{reverse('company:detail', kwargs={'pk': company_id})}#certificates")
    
    # GET zahtev - prikaži formu sa postojećim podacima
    context = {
        'company': company,
        'certificate': certificate,
        'title': f'Izmena sertifikata {certificate.certificate_number}',
        'status_choices': Certificate.STATUS_CHOICES,
    }
    return render(request, 'company/certificate-form.html', context)


def certificate_delete(request, company_id, pk):
    """Brisanje sertifikata"""
    company = get_object_or_404(Company, pk=company_id)
    certificate = get_object_or_404(Certificate, pk=pk, company=company)
    
    if request.method == 'POST':
        certificate_number = certificate.certificate_number
        try:
            certificate.delete()
            messages.success(request, f'Sertifikat {certificate_number} je uspešno obrisan.')
        except Exception as e:
            messages.error(request, f'Greška pri brisanju sertifikata: {str(e)}')
        
        # Vrati na tab Sertifikati
        return redirect(f"{reverse('company:detail', kwargs={'pk': company_id})}#certificates")
    
    # GET zahtev - prikaži potvrdu brisanja
    context = {
        'company': company,
        'certificate': certificate,
        'title': f'Brisanje sertifikata {certificate.certificate_number}',
    }
    return render(request, 'company/certificate-confirm-delete.html', context)


@require_POST
def certificate_ajax_create(request, company_id):
    """AJAX kreiranje sertifikata"""
    company = get_object_or_404(Company, pk=company_id)
    
    certificate_number = request.POST.get('certificate_number', '').strip()
    status = request.POST.get('status', 'pending')
    issue_date = request.POST.get('issue_date') or None
    expiry_date = request.POST.get('expiry_date') or None
    suspension_until_date = request.POST.get('suspension_until_date') or None
    notes = request.POST.get('notes', '').strip()
    
    if not certificate_number:
        return JsonResponse({'success': False, 'error': 'Broj sertifikata je obavezan.'})
    
    if Certificate.objects.filter(certificate_number=certificate_number).exists():
        return JsonResponse({'success': False, 'error': f'Sertifikat sa brojem {certificate_number} već postoji.'})
    
    try:
        certificate = Certificate.objects.create(
            company=company,
            certificate_number=certificate_number,
            status=status,
            issue_date=issue_date,
            expiry_date=expiry_date,
            suspension_until_date=suspension_until_date,
            notes=notes
        )
        return JsonResponse({
            'success': True,
            'message': f'Sertifikat {certificate_number} je uspešno kreiran.',
            'certificate': {
                'id': certificate.id,
                'certificate_number': certificate.certificate_number,
                'status': certificate.status,
                'status_display': certificate.get_status_display(),
            }
        })
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})


@require_POST
def certificate_ajax_delete(request, company_id, pk):
    """AJAX brisanje sertifikata"""
    company = get_object_or_404(Company, pk=company_id)
    certificate = get_object_or_404(Certificate, pk=pk, company=company)
    
    certificate_number = certificate.certificate_number
    try:
        certificate.delete()
        return JsonResponse({
            'success': True,
            'message': f'Sertifikat {certificate_number} je uspešno obrisan.'
        })
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})
