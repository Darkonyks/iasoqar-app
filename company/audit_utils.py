from django.db.models import Q
from .auditor_models import Auditor, AuditorStandard, AuditorStandardIAFEACCode
from .standard_models import StandardDefinition, CompanyStandard
from .cycle_models import CertificationCycle, CycleStandard, CycleAudit
from .iaf_models import IAFEACCode, CompanyIAFEACCode

def get_qualified_auditors_for_company(company_id):
    """
    Vraća listu auditora koji su kvalifikovani za standarde koje kompanija ima.
    
    Args:
        company_id: ID kompanije za koju tražimo kvalifikovane auditore
        
    Returns:
        dict: Rečnik gde su ključevi ID-jevi standarda, a vrednosti su liste auditora
              koji su kvalifikovani za taj standard
    """
    # Dobijamo sve standarde koje kompanija ima
    company_standards = CompanyStandard.objects.filter(company_id=company_id).select_related('standard_definition')
    
    if not company_standards:
        return {}
    
    # Izvlačimo ID-jeve definicija standarda
    standard_ids = [cs.standard_definition_id for cs in company_standards]
    
    # Rezultat će biti rečnik gde su ključevi ID-jevi standarda, a vrednosti su liste auditora
    qualified_auditors = {}
    
    # Za svaki standard, pronalazimo auditore koji su kvalifikovani
    for standard_id in standard_ids:
        # Pronalazimo auditore koji imaju kvalifikacije za ovaj standard
        auditor_standards = AuditorStandard.objects.filter(
            standard_id=standard_id
        ).select_related('auditor')
        
        # Dodajemo auditore u rezultat
        qualified_auditors[standard_id] = [as_obj.auditor for as_obj in auditor_standards]
    
    return qualified_auditors

def is_auditor_qualified_for_company(auditor_id, company_id):
    """
    Proverava da li je auditor kvalifikovan za standarde koje kompanija ima.
    
    Args:
        auditor_id: ID auditora
        company_id: ID kompanije
        
    Returns:
        tuple: (bool, list) - Da li je auditor kvalifikovan i lista standarda za koje nije kvalifikovan
    """
    # Dobijamo sve standarde koje kompanija ima
    company_standards = CompanyStandard.objects.filter(company_id=company_id).select_related('standard_definition')
    
    if not company_standards:
        return True, []  # Ako kompanija nema standarde, auditor je kvalifikovan
    
    # Dobijamo sve standarde za koje je auditor kvalifikovan
    auditor_standards = AuditorStandard.objects.filter(auditor_id=auditor_id).values_list('standard_id', flat=True)
    
    # Proveravamo da li auditor ima sve standarde koje kompanija ima
    missing_standards = []
    for cs in company_standards:
        if cs.standard_definition_id not in auditor_standards:
            missing_standards.append(cs.standard_definition)
    
    # Auditor je kvalifikovan ako nema standarda koji nedostaju
    is_qualified = len(missing_standards) == 0
    
    return is_qualified, missing_standards

def is_auditor_qualified_for_audit(auditor_id, audit_id):
    """
    Proverava da li je auditor kvalifikovan za audit na osnovu standarda u ciklusu sertifikacije.
    
    Args:
        auditor_id: ID auditora
        audit_id: ID audita
        
    Returns:
        tuple: (bool, list) - Da li je auditor kvalifikovan i lista standarda za koje nije kvalifikovan
    """
    # Dobijamo audit i povezani ciklus sertifikacije
    try:
        audit = CycleAudit.objects.get(id=audit_id)
    except CycleAudit.DoesNotExist:
        return False, []
    
    # Dobijamo standarde u ciklusu sertifikacije
    cycle_standards = CycleStandard.objects.filter(
        certification_cycle=audit.certification_cycle
    ).select_related('standard_definition')
    
    if not cycle_standards:
        return True, []  # Ako nema standarda u ciklusu, auditor je kvalifikovan
    
    # Dobijamo sve standarde za koje je auditor kvalifikovan
    auditor_standards = AuditorStandard.objects.filter(auditor_id=auditor_id).values_list('standard_id', flat=True)
    
    # Proveravamo da li auditor ima sve standarde u ciklusu
    missing_standards = []
    for cs in cycle_standards:
        if cs.standard_definition_id not in auditor_standards:
            missing_standards.append(cs.standard_definition)
    
    # Auditor je kvalifikovan ako nema standarda koji nedostaju
    is_qualified = len(missing_standards) == 0
    
    return is_qualified, missing_standards

def get_qualified_auditors_for_audit(audit_id):
    """
    Vraća listu auditora koji su kvalifikovani za standarde u ciklusu sertifikacije.
    
    Args:
        audit_id: ID audita
        
    Returns:
        list: Lista auditora koji su kvalifikovani za sve standarde u ciklusu
    """
    # Dobijamo audit i povezani ciklus sertifikacije
    try:
        audit = CycleAudit.objects.get(id=audit_id)
    except CycleAudit.DoesNotExist:
        return []
    
    # Dobijamo standarde u ciklusu sertifikacije
    cycle_standards = CycleStandard.objects.filter(
        certification_cycle=audit.certification_cycle
    ).select_related('standard_definition')
    
    if not cycle_standards:
        # Ako nema standarda u ciklusu, svi auditori su kvalifikovani
        return Auditor.objects.all()
    
    # Izvlačimo ID-jeve definicija standarda
    standard_ids = [cs.standard_definition_id for cs in cycle_standards]
    
    # Pronalazimo auditore koji imaju kvalifikacije za SVE standarde u ciklusu
    qualified_auditors = []
    all_auditors = Auditor.objects.all()
    
    for auditor in all_auditors:
        # Dobijamo standarde za koje je auditor kvalifikovan
        auditor_standard_ids = set(AuditorStandard.objects.filter(
            auditor=auditor
        ).values_list('standard_id', flat=True))
        
        # Proveravamo da li auditor ima sve potrebne standarde
        if all(std_id in auditor_standard_ids for std_id in standard_ids):
            qualified_auditors.append(auditor)
    
    return qualified_auditors


def verify_auditor_iaf_eac_codes(auditor_id, company_id, standard_id=None):
    """
    Proverava da li auditor ima sve IAF/EAC kodove koje kompanija ima za određeni standard.
    
    Args:
        auditor_id: ID auditora
        company_id: ID kompanije
        standard_id: ID standarda (opciono, ako je None proveravaju se svi standardi)
        
    Returns:
        tuple: (bool, list) - Da li auditor ima sve potrebne kodove i lista kodova koji nedostaju
    """
    # Dobijamo sve IAF/EAC kodove koje kompanija ima
    company_iaf_eac_codes = CompanyIAFEACCode.objects.filter(
        company_id=company_id
    ).select_related('iaf_eac_code')
    
    if not company_iaf_eac_codes:
        return True, []  # Ako kompanija nema IAF/EAC kodove, auditor je kvalifikovan
    
    # Dobijamo sve standarde auditora
    auditor_standards_query = AuditorStandard.objects.filter(auditor_id=auditor_id)
    
    # Ako je naveden specifičan standard, filtriramo samo za taj standard
    if standard_id:
        auditor_standards_query = auditor_standards_query.filter(standard_id=standard_id)
    
    auditor_standards = list(auditor_standards_query.select_related('standard'))
    
    if not auditor_standards:
        # Ako auditor nema standarde, nije kvalifikovan za nijedan IAF/EAC kod
        return False, [code.iaf_eac_code for code in company_iaf_eac_codes]
    
    # Dobijamo sve IAF/EAC kodove koje auditor ima za svoje standarde
    auditor_iaf_eac_codes = set()
    for auditor_standard in auditor_standards:
        codes = AuditorStandardIAFEACCode.objects.filter(
            auditor_standard=auditor_standard
        ).values_list('iaf_eac_code_id', flat=True)
        auditor_iaf_eac_codes.update(codes)
    
    # Proveravamo da li auditor ima sve IAF/EAC kodove koje kompanija ima
    missing_codes = []
    for company_code in company_iaf_eac_codes:
        if company_code.iaf_eac_code_id not in auditor_iaf_eac_codes:
            missing_codes.append(company_code.iaf_eac_code)
    
    # Auditor je kvalifikovan ako nema kodova koji nedostaju
    is_qualified = len(missing_codes) == 0
    
    return is_qualified, missing_codes
