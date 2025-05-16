from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.shortcuts import get_object_or_404
from django.contrib.auth.decorators import login_required
from .standard_models import CompanyStandard

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
