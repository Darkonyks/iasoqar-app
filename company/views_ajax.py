from django.http import JsonResponse
from django.views.decorators.http import require_POST, require_GET
from django.shortcuts import get_object_or_404
from django.contrib.auth.decorators import login_required
from .standard_models import CompanyStandard
from .models import Company
from .iaf_models import IAFEACCode, CompanyIAFEACCode

@require_POST
@login_required
def delete_standard(request):
    """
    AJAX view funkcija za brisanje standarda kompanije.
    Prima ID standarda kao POST parametar i briše ga iz baze.
    Vraća JSON odgovor o statusu operacije.
    """
    standard_id = request.POST.get('standard_id')
    
    if not standard_id:
        return JsonResponse({
            'success': False,
            'message': 'ID standarda nije prosleđen.'
        }, status=400)
    
    try:
        standard = get_object_or_404(CompanyStandard, id=standard_id)
        
        # Sačuvaj ime standarda za povratnu informaciju
        standard_name = str(standard.standard_definition)
        company_name = standard.company.name
        
        # Obriši standard
        standard.delete()
        
        return JsonResponse({
            'success': True,
            'message': f'Standard {standard_name} za kompaniju {company_name} je uspešno obrisan.',
            'deleted_id': standard_id
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Greška pri brisanju standarda: {str(e)}'
        }, status=500)


@require_POST
@login_required
def add_iaf_eac_code(request, company_id):
    """
    AJAX view funkcija za dodavanje IAF/EAC koda kompaniji.
    Prima company_id kao parametar u URL-u i podatke kao POST parametre.
    Vraća JSON odgovor o statusu operacije.
    """
    try:
        # Dohvati kompaniju
        company = get_object_or_404(Company, id=company_id)
        
        # Dohvati podatke iz POST zahteva
        iaf_eac_code_id = request.POST.get('iaf_eac_code')
        is_primary = request.POST.get('is_primary') == 'true'
        notes = request.POST.get('notes', '')
        
        # Validacija podataka
        if not iaf_eac_code_id:
            return JsonResponse({
                'success': False,
                'error': 'Morate izabrati IAF/EAC kod.'
            }, status=400)
        
        # Dohvati IAF/EAC kod
        iaf_eac_code = get_object_or_404(IAFEACCode, id=iaf_eac_code_id)
        
        # Proveri da li veza već postoji
        if CompanyIAFEACCode.objects.filter(company=company, iaf_eac_code=iaf_eac_code).exists():
            return JsonResponse({
                'success': False,
                'error': f'Kompanija već ima dodeljen ovaj IAF/EAC kod ({iaf_eac_code}).'
            }, status=400)
        
        # Kreiraj novu vezu između kompanije i IAF/EAC koda
        company_iaf_eac = CompanyIAFEACCode.objects.create(
            company=company,
            iaf_eac_code=iaf_eac_code,
            is_primary=is_primary,
            notes=notes
        )
        
        return JsonResponse({
            'success': True,
            'message': f'IAF/EAC kod {iaf_eac_code} je uspešno dodat kompaniji {company.name}.',
            'id': company_iaf_eac.id,
            'iaf_code': iaf_eac_code.iaf_code,
            'description': iaf_eac_code.description,
            'is_primary': company_iaf_eac.is_primary,
            'notes': company_iaf_eac.notes
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': f'Greška pri dodavanju IAF/EAC koda: {str(e)}'
        }, status=500)


@require_POST
@login_required
def delete_iaf_eac_code(request, company_id=None, code_id=None):
    """
    AJAX view funkcija za brisanje IAF/EAC koda kompanije.
    Prima ID kompanije i ID koda kao URL parametre ili kao POST parametre.
    Vraća JSON odgovor o statusu operacije.
    """
    # Ako nije prosleđen code_id kroz URL, probaj da ga dobiješ iz POST parametara
    if code_id is None:
        code_id = request.POST.get('code_id')
    
    if not code_id:
        return JsonResponse({
            'success': False,
            'message': 'ID IAF/EAC koda nije prosleđen.'
        }, status=400)
    
    try:
        # Ako je prosleđen company_id, koristi ga za dodatnu validaciju
        if company_id:
            company_iaf_eac = get_object_or_404(CompanyIAFEACCode, id=code_id, company_id=company_id)
        else:
            company_iaf_eac = get_object_or_404(CompanyIAFEACCode, id=code_id)
        
        # Sačuvaj informacije za povratnu poruku
        code_name = str(company_iaf_eac.iaf_eac_code)
        company_name = company_iaf_eac.company.name
        
        # Obriši vezu
        company_iaf_eac.delete()
        
        return JsonResponse({
            'success': True,
            'message': f'IAF/EAC kod {code_name} za kompaniju {company_name} je uspešno obrisan.',
            'deleted_id': code_id
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Greška pri brisanju IAF/EAC koda: {str(e)}'
        }, status=500)


@require_POST
@login_required
def update_iaf_eac_primary(request, company_id=None, code_id=None):
    """
    AJAX view funkcija za ažuriranje primarnog IAF/EAC koda kompanije.
    Prima ID kompanije i ID koda kao URL parametre ili kao POST parametre.
    Vraća JSON odgovor o statusu operacije.
    """
    # Ako nije prosleđen code_id kroz URL, probaj da ga dobiješ iz POST parametara
    if code_id is None:
        code_id = request.POST.get('code_id')
    
    if not code_id:
        return JsonResponse({
            'success': False,
            'message': 'ID IAF/EAC koda nije prosleđen.'
        }, status=400)
    
    try:
        # Ako je prosleđen company_id, koristi ga za dodatnu validaciju
        if company_id:
            company_iaf_eac = get_object_or_404(CompanyIAFEACCode, id=code_id, company_id=company_id)
        else:
            company_iaf_eac = get_object_or_404(CompanyIAFEACCode, id=code_id)
        
        # Prvo resetuj sve primarne kodove za ovu kompaniju
        CompanyIAFEACCode.objects.filter(company=company_iaf_eac.company, is_primary=True).update(is_primary=False)
        
        # Sada postavi ovaj kod kao primarni
        company_iaf_eac.is_primary = True
        company_iaf_eac.save()
        
        return JsonResponse({
            'success': True,
            'message': f'IAF/EAC kod {company_iaf_eac.iaf_eac_code} je postavljen kao primarni za kompaniju {company_iaf_eac.company.name}.'
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Greška pri ažuriranju primarnog IAF/EAC koda: {str(e)}'
        }, status=500)


@require_GET
@login_required
def list_iaf_eac_codes(request, company_id):
    """
    AJAX view funkcija za dobijanje liste IAF/EAC kodova kompanije.
    Prima ID kompanije kao URL parametar.
    Vraća JSON odgovor sa listom kodova.
    """
    try:
        # Dohvati kompaniju
        company = get_object_or_404(Company, id=company_id)
        
        # Dohvati sve IAF/EAC kodove za kompaniju
        company_iaf_eac_codes = CompanyIAFEACCode.objects.filter(company=company)
        
        codes_data = []
        for code in company_iaf_eac_codes:
            codes_data.append({
                'id': code.id,
                'iaf_code': code.iaf_eac_code.iaf_code,
                'description': code.iaf_eac_code.description,
                'is_primary': code.is_primary,
                'notes': code.notes or ''
            })
        
        return JsonResponse({
            'success': True,
            'codes': codes_data
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Greška pri dohvatanju IAF/EAC kodova: {str(e)}'
        }, status=500)
