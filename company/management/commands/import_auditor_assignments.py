from django.core.management.base import BaseCommand
from django.db import transaction
from company.auditor_models import Auditor, AuditorStandard, AuditorStandardIAFEACCode
from company.standard_models import StandardDefinition
from company.iaf_models import IAFEACCode
import pandas as pd


class Command(BaseCommand):
    help = 'Import auditor assignments (categories, TA codes, standards, and EAC codes) from Excel file'
    
    # Mapiranje kodova standarda iz Excela na pun naziv
    STANDARD_MAPPING = {
        '9001': 'ISO 9001:2015',
        '14001': 'ISO 14001:2015',
        '45001': 'ISO 45001:2018',
        '27001': 'ISO 27001:2022',
        '22000': 'ISO 22000:2018',
        '13485': 'ISO 13485:2016',
        '50001': 'ISO 50001:2018',
        '20000': 'ISO 20000-1:2018',
        '22301': 'ISO 22301:2019',
        '37001': 'ISO 37001:2016',
        '17025': 'ISO 17025:2017',
        '17020': 'ISO 17020:2012',
        '17021': 'ISO 17021-1:2015',
        '17024': 'ISO 17024:2012',
        '17065': 'ISO 17065:2012',
        'HACCP': 'HACCP',
        'FSSC22000': 'FSSC 22000 v5.1',
        'IFS': 'IFS Food v7',
        'BRC': 'BRC Food v9',
        # Dodatni kodovi koji se pojavljuju u tabeli
        '1090': 'ISO 1090',
        '90001': 'ISO 90001',
        '22716': 'ISO 22716',
    }

    def normalize_eac_code(self, eac_code):
        """
        Normalizuje EAC kod - dodaje vodeću nulu ako je potrebno.
        Primer: '6a' -> '06a', '7b' -> '07b', '28a' -> '28a'
        """
        if not eac_code:
            return eac_code
        
        # Izdvoji numerički deo i slovna oznaka
        import re
        match = re.match(r'^(\d+)([a-z]*)$', eac_code.lower())
        if match:
            number = match.group(1)
            letter = match.group(2)
            
            # Ako je broj jednocifren, dodaj vodeću nulu
            if len(number) == 1:
                return f'0{number}{letter}'
            else:
                return f'{number}{letter}'
        
        # Ako ne odgovara patternu, vrati originalni kod
        return eac_code

    def add_arguments(self, parser):
        parser.add_argument('excel_file', type=str, help='Path to Excel file')
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Run without making changes to database',
        )
        parser.add_argument(
            '--clear-existing',
            action='store_true',
            help='Clear existing auditor assignments before import',
        )

    def handle(self, *args, **options):
        excel_file = options['excel_file']
        dry_run = options['dry_run']
        clear_existing = options['clear_existing']
        
        if dry_run:
            self.stdout.write(
                self.style.WARNING('DRY RUN MODE - No changes will be made to database')
            )

        try:
            # Učitaj Excel fajl
            df = pd.read_excel(excel_file)
            
            # Proveri da li postoje potrebne kolone
            required_columns = ['Auditor', 'Kategorija', 'TA', 'STANDARD', 'EAC']
            missing_columns = [col for col in required_columns if col not in df.columns]
            
            if missing_columns:
                self.stdout.write(
                    self.style.ERROR(f'Missing columns: {", ".join(missing_columns)}')
                )
                return
            
            # Parse podatke
            auditor_data = self.parse_excel_data(df)
            
            self.stdout.write(f'Pronađeno {len(auditor_data)} jedinstvenih auditora')
            
            if not dry_run:
                with transaction.atomic():
                    if clear_existing:
                        self.clear_existing_data()
                    
                    self.import_data(auditor_data)
            else:
                # Samo prikaži šta bi se importovalo
                self.preview_import(auditor_data)
                        
        except FileNotFoundError:
            self.stdout.write(
                self.style.ERROR(f'File not found: {excel_file}')
            )
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Error processing file: {str(e)}')
            )
            import traceback
            traceback.print_exc()

    def parse_excel_data(self, df):
        """Parse Excel data and group by auditor"""
        auditor_dict = {}
        
        for idx, row in df.iterrows():
            auditor_name = str(row['Auditor']).strip()
            category = str(row['Kategorija']).strip()
            ta_code = str(row['TA']).strip() if pd.notna(row['TA']) else None
            standard = str(row['STANDARD']).strip() if pd.notna(row['STANDARD']) else None
            eac_code = str(row['EAC']).strip() if pd.notna(row['EAC']) else None
            
            # Kreiraj jedinstveni ključ za auditora
            key = auditor_name
            
            if key not in auditor_dict:
                auditor_dict[key] = {
                    'name': auditor_name,
                    'category': category,
                    'ta_codes': set(),
                    'standards': set(),
                    'eac_codes': set(),
                    'ta_eac_mapping': {}  # Mapiranje TA -> EAC kodovi
                }
            
            # Dodaj TA kod
            if ta_code:
                auditor_dict[key]['ta_codes'].add(ta_code)
                
                # Kreiraj mapiranje TA -> EAC
                if ta_code not in auditor_dict[key]['ta_eac_mapping']:
                    auditor_dict[key]['ta_eac_mapping'][ta_code] = set()
                
                if eac_code:
                    auditor_dict[key]['ta_eac_mapping'][ta_code].add(eac_code)
            
            # Dodaj standard
            if standard:
                auditor_dict[key]['standards'].add(standard)
            
            # Dodaj EAC kod
            if eac_code:
                auditor_dict[key]['eac_codes'].add(eac_code)
        
        return list(auditor_dict.values())

    def clear_existing_data(self):
        """Clear existing auditor assignment data"""
        self.stdout.write('Brisanje postojećih dodela auditora...')
        
        # Briši samo veze, ne i same auditore
        deleted_standard_links = AuditorStandard.objects.count()
        deleted_eac_links = AuditorStandardIAFEACCode.objects.count()
        
        AuditorStandardIAFEACCode.objects.all().delete()
        AuditorStandard.objects.all().delete()
        
        self.stdout.write(f'Obrisano {deleted_standard_links} veza sa standardima i {deleted_eac_links} veza sa EAC kodovima')

    def get_or_create_standard(self, standard_code):
        """
        Pronađi ili kreiraj standard na osnovu koda.
        Prvo pokušava da pronađe po kodu, zatim kreira ako ne postoji.
        """
        # Pokušaj da pronađeš postojeći standard po kodu
        try:
            return StandardDefinition.objects.get(code=standard_code)
        except StandardDefinition.DoesNotExist:
            pass
        
        # Ako ne postoji, kreiraj novi standard
        full_name = self.STANDARD_MAPPING.get(standard_code, f'ISO {standard_code}')
        
        # Proveri da li postoji u STANDARD_CHOICES
        standard_choice = None
        for choice_code, choice_name in StandardDefinition.STANDARD_CHOICES:
            if choice_code == full_name:
                standard_choice = full_name
                break
        
        # Kreiraj standard
        standard = StandardDefinition.objects.create(
            code=standard_code,
            name=full_name,
            standard=standard_choice,  # Može biti None ako nije u choices
            description=f'Automatski kreiran tokom importa auditora',
            active=True
        )
        
        self.stdout.write(
            self.style.SUCCESS(f'      ✓ Kreiran novi standard: {standard_code} - {full_name}')
        )
        
        return standard

    def import_data(self, auditor_data):
        """Import parsed data into database"""
        created_auditors = 0
        updated_auditors = 0
        assigned_standards = 0
        assigned_eac_codes = 0
        
        for data in auditor_data:
            auditor_name = data['name']
            category = data['category']
            ta_codes = data['ta_codes']
            standards = data['standards']
            eac_codes = data['eac_codes']
            
            # Mapiranje kategorija iz Excela na Django choices
            # Normalizuj kategoriju - pretvori u lowercase i ukloni razmake za lakše mapiranje
            category_normalized = category.lower().strip()
            
            category_mapping = {
                'lead auditor': Auditor.CATEGORY_LEAD_AUDITOR,
                'lead_auditor': Auditor.CATEGORY_LEAD_AUDITOR,
                'auditor': Auditor.CATEGORY_AUDITOR,
                'technical expert': Auditor.CATEGORY_TECHNICAL_EXPERT,
                'technical_expert': Auditor.CATEGORY_TECHNICAL_EXPERT,
                'tehnički ekspert': Auditor.CATEGORY_TECHNICAL_EXPERT,
                'trainer': Auditor.CATEGORY_TRAINER,
                'trainee': Auditor.CATEGORY_TRAINER,  # Trainee -> Trainer
            }
            
            django_category = category_mapping.get(category_normalized, Auditor.CATEGORY_AUDITOR)
            
            # Kreiraj ili pronađi auditora
            auditor, created = Auditor.objects.get_or_create(
                ime_prezime=auditor_name,
                defaults={
                    'kategorija': django_category,
                    'email': f'{auditor_name.lower().replace(" ", ".")}@example.com',  # Placeholder
                    'telefon': 'N/A',  # Placeholder
                }
            )
            
            if created:
                created_auditors += 1
                self.stdout.write(f'  Kreiran auditor: {auditor_name} ({auditor.get_kategorija_display()})')
            else:
                updated_auditors += 1
                # Ažuriraj kategoriju ako je potrebno
                if auditor.kategorija != django_category:
                    auditor.kategorija = django_category
                    auditor.save()
                self.stdout.write(f'  Pronađen auditor: {auditor_name} ({auditor.get_kategorija_display()})')
            
            # Dodeli TA kodove (uzmi prvi ako ih ima više)
            if ta_codes:
                primary_ta = sorted(ta_codes)[0]  # Uzmi prvi TA kod
                auditor.technical_area_code = primary_ta
                auditor.save()
                self.stdout.write(f'    TA kod: {primary_ta}')
            
            # Različita logika za Technical Expert vs ostale kategorije
            if django_category == Auditor.CATEGORY_TECHNICAL_EXPERT:
                # Technical Expert: samo direktni EAC kodovi, BEZ standarda
                self.stdout.write(f'    Technical Expert - dodeljujem samo EAC kodove (direktno)')
                for eac_code_str in eac_codes:
                    # Normalizuj EAC kod (dodaj vodeću nulu ako je potrebno)
                    normalized_code = self.normalize_eac_code(eac_code_str)
                    try:
                        eac_code = IAFEACCode.objects.get(iaf_code=normalized_code)
                        from company.auditor_models import AuditorIAFEACCode
                        AuditorIAFEACCode.objects.get_or_create(
                            auditor=auditor,
                            iaf_eac_code=eac_code,
                            defaults={'notes': f'Uvezen iz tabele - TA: {auditor.technical_area_code}'}
                        )
                        assigned_eac_codes += 1
                        self.stdout.write(f'      ✓ EAC kod: {eac_code_str} -> {normalized_code}')
                    except IAFEACCode.DoesNotExist:
                        self.stdout.write(
                            self.style.WARNING(f'      ✗ EAC kod "{eac_code_str}" (normalizovan: "{normalized_code}") ne postoji u bazi')
                        )
            else:
                # Ostale kategorije: dodeljuju se standardi + EAC kodovi povezani sa standardima
                if 'SVI' in standards or 'ALL' in standards:
                    # Dodeli sve standarde
                    all_standards = StandardDefinition.objects.filter(active=True)
                    for standard in all_standards:
                        auditor_standard, created = AuditorStandard.objects.get_or_create(
                            auditor=auditor,
                            standard=standard,
                            defaults={'napomena': 'Uvezen iz tabele - SVI standardi'}
                        )
                        
                        if created:
                            assigned_standards += 1
                        
                        # Dodeli EAC kodove ovom standardu
                        for eac_code_str in eac_codes:
                            # Normalizuj EAC kod (dodaj vodeću nulu ako je potrebno)
                            normalized_code = self.normalize_eac_code(eac_code_str)
                            try:
                                eac_code = IAFEACCode.objects.get(iaf_code=normalized_code)
                                AuditorStandardIAFEACCode.objects.get_or_create(
                                    auditor_standard=auditor_standard,
                                    iaf_eac_code=eac_code,
                                    defaults={'notes': f'Uvezen iz tabele - TA: {auditor.technical_area_code}'}
                                )
                                assigned_eac_codes += 1
                            except IAFEACCode.DoesNotExist:
                                self.stdout.write(
                                    self.style.WARNING(f'    EAC kod "{eac_code_str}" (normalizovan: "{normalized_code}") ne postoji u bazi')
                                )
                    
                    self.stdout.write(f'    Dodeljeno: SVI standardi ({all_standards.count()})')
                else:
                    # Dodeli specifične standarde
                    for standard_code in standards:
                        # Koristi get_or_create_standard umesto try/except
                        standard = self.get_or_create_standard(standard_code)
                        
                        auditor_standard, created = AuditorStandard.objects.get_or_create(
                            auditor=auditor,
                            standard=standard,
                            defaults={'napomena': 'Uvezen iz tabele'}
                        )
                        
                        if created:
                            assigned_standards += 1
                        
                        # Dodeli EAC kodove ovom standardu
                        for eac_code_str in eac_codes:
                            # Normalizuj EAC kod (dodaj vodeću nulu ako je potrebno)
                            normalized_code = self.normalize_eac_code(eac_code_str)
                            try:
                                eac_code = IAFEACCode.objects.get(iaf_code=normalized_code)
                                AuditorStandardIAFEACCode.objects.get_or_create(
                                    auditor_standard=auditor_standard,
                                    iaf_eac_code=eac_code,
                                    defaults={'notes': f'Uvezen iz tabele - TA: {auditor.technical_area_code}'}
                                )
                                assigned_eac_codes += 1
                            except IAFEACCode.DoesNotExist:
                                self.stdout.write(
                                    self.style.WARNING(f'    EAC kod "{eac_code_str}" (normalizovan: "{normalized_code}") ne postoji u bazi')
                                )
                        
                        self.stdout.write(f'    Dodeljen standard: {standard.code}')
        
        self.stdout.write(
            self.style.SUCCESS(
                f'\nImport završen!\n'
                f'Kreirano auditora: {created_auditors}\n'
                f'Ažurirano auditora: {updated_auditors}\n'
                f'Dodeljeno standarda: {assigned_standards}\n'
                f'Dodeljeno EAC kodova: {assigned_eac_codes}'
            )
        )

    def preview_import(self, auditor_data):
        """Preview what would be imported"""
        self.stdout.write(self.style.WARNING('PREVIEW - Šta bi se importovalo:'))
        
        for i, data in enumerate(auditor_data[:10]):  # Prikaži prvih 10
            self.stdout.write(f'\n{i+1}. Auditor: {data["name"]}')
            self.stdout.write(f'   Kategorija: {data["category"]}')
            self.stdout.write(f'   TA kodovi: {", ".join(sorted(data["ta_codes"]))}')
            self.stdout.write(f'   Standardi: {", ".join(sorted(data["standards"]))}')
            self.stdout.write(f'   EAC kodovi: {", ".join(sorted(data["eac_codes"]))}')
        
        if len(auditor_data) > 10:
            self.stdout.write(f'\n... i još {len(auditor_data) - 10} auditora')
        
        self.stdout.write(f'\nUkupno bi se obradilo {len(auditor_data)} auditora.')
