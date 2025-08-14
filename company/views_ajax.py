from django.http import JsonResponse
from django.views.decorators.http import require_POST, require_GET
from django.shortcuts import get_object_or_404
from django.contrib.auth.decorators import login_required
from django.utils import timezone
import logging
import json
from datetime import datetime, time
from .standard_models import CompanyStandard
from .models import Company, Appointment
from .iaf_models import IAFEACCode, CompanyIAFEACCode
from .cycle_models import CertificationCycle, CycleAudit, AuditDay

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


@require_GET
@login_required
def certification_cycle_json(request, pk):
    """
    API endpoint za dohvatanje podataka o certifikacionom ciklusu u JSON formatu.
    Vraća podatke o ciklusu i povezanom auditu.
    """
    logger = logging.getLogger('django')
    logger.info(f"Dohvatanje podataka o certifikacionom ciklusu ID={pk}")
    
    try:
        # Dohvatamo certifikacioni ciklus
        cycle = get_object_or_404(CertificationCycle, pk=pk)
        
        # Pripremamo osnovne podatke o ciklusu
        cycle_data = {
            'id': cycle.id,
            'company_name': cycle.company.name,
            'planirani_datum': cycle.planirani_datum.isoformat() if cycle.planirani_datum else None,
            'status': cycle.status,
            'status_display': dict(cycle.CYCLE_STATUS_CHOICES)[cycle.status],
            'is_integrated_system': cycle.is_integrated_system,
            'notes': cycle.notes or '',
            'created_at': cycle.created_at.isoformat(),
            'updated_at': cycle.updated_at.isoformat()
        }
        
        # Dohvatamo povezane standarde
        standards = []
        for cycle_standard in cycle.cycle_standards.all():
            standards.append({
                'id': cycle_standard.id,
                'code': cycle_standard.standard_definition.code,
                'name': cycle_standard.standard_definition.name
            })
        cycle_data['standards'] = standards
        
        # Dohvatamo povezane audite
        audit_data = None
        # Pokušavamo da pronađemo audit koji odgovara ID-u iz URL-a događaja
        # Prvo proveravamo da li postoji ID audita u URL parametrima
        audit_id = request.GET.get('audit_id')
        
        if audit_id:
            try:
                audit = CycleAudit.objects.get(pk=audit_id, certification_cycle=cycle)
                logger.info(f"Pronađen audit ID={audit_id} za ciklus ID={pk}")
            except CycleAudit.DoesNotExist:
                audit = None
                logger.warning(f"Nije pronađen audit ID={audit_id} za ciklus ID={pk}")
        else:
            # Ako nije prosleđen ID audita, uzimamo poslednji audit u ciklusu
            audit = cycle.audits.order_by('-planned_date').first()
            logger.info(f"Uzimamo poslednji audit za ciklus ID={pk}: {audit.id if audit else None}")
        
        if audit:
            audit_data = {
                'id': audit.id,
                'audit_type': audit.audit_type,
                'audit_type_display': dict(audit.AUDIT_TYPE_CHOICES)[audit.audit_type],
                'audit_status': audit.audit_status,
                'audit_status_display': dict(audit.AUDIT_STATUS_CHOICES)[audit.audit_status],
                'planned_date': audit.planned_date.isoformat() if audit.planned_date else None,
                'actual_date': audit.actual_date.isoformat() if audit.actual_date else None,
                'notes': audit.notes or ''
            }
            
            # Dohvatamo dane audita
            audit_days = []
            for day in audit.audit_days.all().order_by('date'):
                audit_days.append({
                    'id': day.id,
                    'date': day.date.isoformat() if day.date else None,
                    'is_planned': day.is_planned,
                    'is_actual': day.is_actual,
                    'notes': day.notes or ''
                })
            audit_data['audit_days'] = audit_days
        
        # Vraćamo podatke o ciklusu i auditu
        return JsonResponse({
            'cycle': cycle_data,
            'audit': audit_data
        })
    
    except Exception as e:
        import traceback
        logger.error(f"Greška prilikom dohvatanja podataka o certifikacionom ciklusu ID={pk}: {str(e)}")
        logger.error(traceback.format_exc())
        return JsonResponse({'error': str(e)}, status=500)


@require_GET
@login_required
def audit_days_by_audit_id(request, audit_id):
    """
    API endpoint za dohvatanje podataka o danima audita prema ID-u audita.
    Vraća podatke o auditu i povezanim danima audita.
    """
    logger = logging.getLogger('django')
    logger.info(f"Dohvatanje podataka o danima audita za audit ID={audit_id}")
    
    try:
        # Dohvatamo audit
        audit = get_object_or_404(CycleAudit, pk=audit_id)
        
        # Pripremamo osnovne podatke o auditu
        audit_data = {
            'id': audit.id,
            'audit_type': audit.audit_type,
            'audit_type_display': dict(audit.AUDIT_TYPE_CHOICES)[audit.audit_type],
            'audit_status': audit.audit_status,
            'audit_status_display': dict(audit.AUDIT_STATUS_CHOICES)[audit.audit_status],
            'planned_date': audit.planned_date.isoformat() if audit.planned_date else None,
            'actual_date': audit.actual_date.isoformat() if audit.actual_date else None,
            'notes': audit.notes or '',
            'certification_cycle_id': audit.certification_cycle.id,
            'company_name': audit.certification_cycle.company.name
        }
        
        # Dohvatamo dane audita
        audit_days = []
        for day in audit.audit_days.all().order_by('date'):
            audit_days.append({
                'id': day.id,
                'date': day.date.isoformat() if day.date else None,
                'is_planned': day.is_planned,
                'is_actual': day.is_actual,
                'notes': day.notes or ''
            })
        audit_data['audit_days'] = audit_days
        
        # Vraćamo podatke o auditu i danima audita
        return JsonResponse({
            'success': True,
            'audit': audit_data
        })
    
    except Exception as e:
        import traceback
        logger.error(f"Greška prilikom dohvatanja podataka o danima audita za audit ID={audit_id}: {str(e)}")
        logger.error(traceback.format_exc())
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@require_POST
@login_required
def update_event_date(request):
    """
    API endpoint za ažuriranje datuma događaja (audit ili audit day) nakon drag-and-drop operacije.
    Prima podatke o događaju i novom datumu kao POST parametre.
    Vraća JSON odgovor o statusu operacije.
    """
    logger = logging.getLogger('django')
    logger.info(f"Ažuriranje datuma događaja nakon drag-and-drop")
    
    try:
        # Parsiranje JSON podataka iz POST zahteva
        data = json.loads(request.body)
        event_id = data.get('eventId')
        event_type = data.get('eventType')
        new_date = data.get('newDate')
        
        logger.info(f"Primljeni podaci: event_id={event_id}, event_type={event_type}, new_date={new_date}")
        
        # Validacija podataka
        if not event_id or not event_type or not new_date:
            return JsonResponse({
                'success': False,
                'error': 'Nedostaju obavezni parametri (eventId, eventType, newDate).'
            }, status=400)
        
        # Parsiranje datuma
        try:
            new_date_obj = datetime.fromisoformat(str(new_date).replace('Z', '+00:00'))
        except ValueError:
            return JsonResponse({
                'success': False,
                'error': 'Neispravan format datuma.'
            }, status=400)

        # Normalizacija na svesno vreme i lokalnu vremensku zonu
        tz = timezone.get_current_timezone()
        aware_dt = timezone.make_aware(new_date_obj, tz) if timezone.is_naive(new_date_obj) else new_date_obj
        local_dt = timezone.localtime(aware_dt, tz)
        
        # Ažuriranje datuma u zavisnosti od tipa događaja
        if event_type == 'audit_day':
            # Ažuriranje datuma audit dana
            audit_day = get_object_or_404(AuditDay, pk=event_id)
            old_date = audit_day.date
            # Koristi lokalni datum (ne UTC) da se izbegne pomeranje za jedan dan
            audit_day.date = local_dt.date()
            audit_day.save()
            
            return JsonResponse({
                'success': True,
                'message': f'Datum audit dana je uspešno ažuriran sa {old_date} na {audit_day.date}.',
                'auditDay': {
                    'id': audit_day.id,
                    'date': audit_day.date.isoformat(),
                    'is_planned': audit_day.is_planned,
                    'is_actual': audit_day.is_actual,
                    'notes': audit_day.notes or ''
                }
            })
            
        elif event_type == 'cycle_audit':
            # Ažuriranje planiranog datuma audita
            audit = get_object_or_404(CycleAudit, pk=event_id)
            old_date = audit.planned_date
            # Koristi lokalni datum (ne UTC) da se izbegne pomeranje za jedan dan
            # Važno: koristimo queryset update da NE bismo pozvali save() i automatsko
            # regenerisanje AuditDay zapisa u CycleAudit.save().
            new_planned = local_dt.date()
            CycleAudit.objects.filter(pk=audit.pk).update(planned_date=new_planned)
            # Ažuriramo instancu samo za odgovor (bez poziva save())
            audit.planned_date = new_planned
            
            return JsonResponse({
                'success': True,
                'message': f'Planirani datum audita je uspešno ažuriran sa {old_date} na {audit.planned_date}.',
                'audit': {
                    'id': audit.id,
                    'planned_date': audit.planned_date.isoformat(),
                    'audit_type': audit.audit_type,
                    'audit_status': audit.audit_status
                }
            })
            
        elif event_type == 'appointment':
            # Ažuriranje datuma početka (i eventualno kraja) termina/sastanka
            appt = get_object_or_404(Appointment, pk=event_id)
            old_start = appt.start_datetime
            old_end = appt.end_datetime

            # Ako je all-day termin, postavi na lokalnu ponoć novog datuma.
            # Inače koristi precizno novo vreme (svestan datetime) koje je client poslao
            if getattr(appt, 'all_day', False):
                new_start_dt = timezone.make_aware(
                    datetime.combine(local_dt.date(), time.min),
                    timezone.get_current_timezone()
                )
            else:
                # Koristi precizni trenutak
                new_start_dt = aware_dt

            appt.start_datetime = new_start_dt

            # Ako postoji kraj, pomeri ga za isti pomak kao i početak (očuvaj trajanje)
            if old_end:
                delta = new_start_dt - old_start
                appt.end_datetime = old_end + delta

            appt.save()

            payload = {
                'id': appt.id,
                'start_datetime': appt.start_datetime.isoformat(),
                'end_datetime': appt.end_datetime.isoformat() if appt.end_datetime else None,
                'all_day': getattr(appt, 'all_day', False),
                'status': getattr(appt, 'status', None)
            }

            return JsonResponse({
                'success': True,
                'message': 'Datum termina je uspešno ažuriran.',
                'appointment': payload
            })
        
        else:
            return JsonResponse({
                'success': False,
                'error': f'Nepodržani tip događaja: {event_type}'
            }, status=400)
    
    except Exception as e:
        import traceback
        logger.error(f"Greška prilikom ažuriranja datuma događaja: {str(e)}")
        logger.error(traceback.format_exc())
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)
