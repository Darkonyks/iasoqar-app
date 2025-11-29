from django.core.management.base import BaseCommand
from django.db import transaction
from company.iaf_models import IAFScopeReference, IAFEACCode
import pandas as pd
import re


class Command(BaseCommand):
    help = 'Import IAF/EAC codes from Excel file'

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
            help='Clear existing IAF/EAC codes before import',
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
            # Učitaj oba sheet-a iz Excel fajla
            sheets_to_load = ['Sheet1', 'Sheet11']
            all_groups = []
            
            for sheet_name in sheets_to_load:
                try:
                    df = pd.read_excel(excel_file, sheet_name=sheet_name)
                    self.stdout.write(f'Učitavam sheet: {sheet_name}')
                    
                    # Parse podatke u grupe
                    groups = self.parse_excel_data(df)
                    all_groups.extend(groups)
                    
                    self.stdout.write(f'  - Pronađeno {len(groups)} grupa u {sheet_name}')
                except ValueError as e:
                    self.stdout.write(
                        self.style.WARNING(f'Sheet "{sheet_name}" nije pronađen, preskačem...')
                    )
            
            groups = all_groups
            self.stdout.write(f'\nUkupno pronađeno {len(groups)} IAF Scope Reference grupa')
            total_codes = sum(len(g['codes']) for g in groups)
            self.stdout.write(f'Ukupno {total_codes} IAF/EAC kodova')
            
            if not dry_run:
                with transaction.atomic():
                    if clear_existing:
                        self.clear_existing_data()
                    
                    self.import_data(groups)
                    
                    if dry_run:
                        # Rollback transaction in dry run mode
                        transaction.set_rollback(True)
            else:
                # Samo prikaži šta bi se importovalo
                self.preview_import(groups)
                        
        except FileNotFoundError:
            self.stdout.write(
                self.style.ERROR(f'File not found: {excel_file}')
            )
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Error processing file: {str(e)}')
            )

    def parse_excel_data(self, df):
        """Parse Excel data into groups"""
        groups = []
        current_scope = None
        current_group = []
        
        for idx, row in df.iterrows():
            # Proveri da li je ovo red sa IAF Scope Reference
            if pd.notna(row['IAF Scope Reference']):
                # Završi prethodnu grupu
                if current_group and current_scope:
                    groups.append({
                        'scope_reference': current_scope,
                        'scope_description': self.extract_scope_description(current_scope),
                        'codes': current_group.copy()
                    })
                
                # Počni novu grupu
                current_scope = row['IAF Scope Reference']
                current_group = []
                
                # Ako ovaj red takođe ima kod, dodaj ga
                if pd.notna(row['IAF/EAC Code']):
                    current_group.append({
                        'code': str(row['IAF/EAC Code']).strip(),
                        'description': str(row['Code Description']).strip() if pd.notna(row['Code Description']) else '',
                        'row': idx
                    })
            
            # Ako je ovo red sa kodom (bez scope reference)
            elif pd.notna(row['IAF/EAC Code']):
                if current_scope:  # Samo ako imamo aktivnu grupu
                    current_group.append({
                        'code': str(row['IAF/EAC Code']).strip(),
                        'description': str(row['Code Description']).strip() if pd.notna(row['Code Description']) else '',
                        'row': idx
                    })
        
        # Dodaj poslednju grupu
        if current_group and current_scope:
            groups.append({
                'scope_reference': current_scope,
                'scope_description': self.extract_scope_description(current_scope),
                'codes': current_group.copy()
            })
        
        return groups

    def extract_scope_description(self, scope_text):
        """Extract scope reference number and description from text like 'IAF 1 Agriculture, forestry and fishing'"""
        # Pattern: IAF [broj] [opis]
        match = re.match(r'IAF\s+(\d+)\s+(.+)', scope_text.strip())
        if match:
            return {
                'reference': match.group(1),
                'description': match.group(2).strip()
            }
        else:
            # Fallback - koristi ceo tekst kao opis
            return {
                'reference': scope_text.strip(),
                'description': scope_text.strip()
            }

    def clear_existing_data(self):
        """Clear existing IAF/EAC data"""
        self.stdout.write('Brisanje postojećih IAF/EAC kodova...')
        
        deleted_codes = IAFEACCode.objects.count()
        deleted_scopes = IAFScopeReference.objects.count()
        
        IAFEACCode.objects.all().delete()
        IAFScopeReference.objects.all().delete()
        
        self.stdout.write(f'Obrisano {deleted_codes} kodova i {deleted_scopes} scope referenci')

    def import_data(self, groups):
        """Import parsed data into database"""
        created_scopes = 0
        created_codes = 0
        
        for group in groups:
            scope_info = group['scope_description']
            
            # Kreiraj ili pronađi IAF Scope Reference
            scope_ref, created = IAFScopeReference.objects.get_or_create(
                reference=scope_info['reference'],
                defaults={'description': scope_info['description']}
            )
            
            if created:
                created_scopes += 1
                self.stdout.write(f'  Kreiran scope: {scope_ref.reference} - {scope_ref.description}')
            
            # Kreiraj IAF/EAC kodove
            for code_data in group['codes']:
                iaf_code, created = IAFEACCode.objects.get_or_create(
                    iaf_code=code_data['code'],
                    defaults={
                        'description': code_data['description'],
                        'iaf_scope_reference': scope_ref
                    }
                )
                
                if created:
                    created_codes += 1
                    if len(code_data['description']) > 50:
                        desc_short = code_data['description'][:47] + '...'
                    else:
                        desc_short = code_data['description']
                    self.stdout.write(f'    Kreiran kod: {iaf_code.iaf_code} - {desc_short}')
                else:
                    self.stdout.write(f'    Kod već postoji: {iaf_code.iaf_code}')
        
        self.stdout.write(
            self.style.SUCCESS(f'Import završen! Kreirano {created_scopes} scope referenci i {created_codes} kodova.')
        )

    def preview_import(self, groups):
        """Preview what would be imported"""
        self.stdout.write(self.style.WARNING('PREVIEW - Šta bi se importovalo:'))
        
        for i, group in enumerate(groups[:5]):  # Prikaži prvih 5 grupa
            scope_info = group['scope_description']
            self.stdout.write(f'\n{i+1}. Scope Reference: {scope_info["reference"]} - {scope_info["description"]}')
            
            for j, code_data in enumerate(group['codes'][:3]):  # Prikaži prva 3 koda
                desc = code_data['description']
                if len(desc) > 60:
                    desc = desc[:57] + '...'
                self.stdout.write(f'   - {code_data["code"]}: {desc}')
            
            if len(group['codes']) > 3:
                self.stdout.write(f'   ... i još {len(group["codes"]) - 3} kodova')
        
        if len(groups) > 5:
            self.stdout.write(f'\n... i još {len(groups) - 5} grupa')
        
        total_codes = sum(len(g['codes']) for g in groups)
        self.stdout.write(f'\nUkupno bi se kreiralo {len(groups)} scope referenci i {total_codes} kodova.')
