from django.core.management.base import BaseCommand
from django.db import transaction
from company.auditor_models import Auditor, AuditorIAFEACCode
from company.iaf_models import IAFEACCode
import csv


class Command(BaseCommand):
    help = 'Import auditor data from CSV file'

    def add_arguments(self, parser):
        parser.add_argument('csv_file', type=str, help='Path to CSV file')
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Run without making changes to database',
        )

    def handle(self, *args, **options):
        csv_file = options['csv_file']
        dry_run = options['dry_run']
        
        if dry_run:
            self.stdout.write(
                self.style.WARNING('DRY RUN MODE - No changes will be made to database')
            )

        try:
            with open(csv_file, 'r', encoding='utf-8') as file:
                reader = csv.DictReader(file)
                
                with transaction.atomic():
                    for row in reader:
                        self.process_row(row, dry_run)
                        
                    if dry_run:
                        # Rollback transaction in dry run mode
                        transaction.set_rollback(True)
                        
        except FileNotFoundError:
            self.stdout.write(
                self.style.ERROR(f'File not found: {csv_file}')
            )
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Error processing file: {str(e)}')
            )

    def process_row(self, row, dry_run):
        """
        Process single row from CSV
        Expected columns: Auditor, Kategorija, TA, STANDARD, EAC, COMMENT
        """
        auditor_name = row.get('Auditor', '').strip()
        category = row.get('Kategorija', '').strip()
        ta_code = row.get('TA', '').strip()
        standard = row.get('STANDARD', '').strip()
        eac_codes = row.get('EAC', '').strip()
        comment = row.get('COMMENT', '').strip()

        if not auditor_name:
            self.stdout.write(
                self.style.WARNING('Skipping row with empty auditor name')
            )
            return

        # Map category from Serbian to model choices
        category_mapping = {
            'Technical Expert': Auditor.CATEGORY_TECHNICAL_EXPERT,
            'Lead Auditor': Auditor.CATEGORY_LEAD_AUDITOR,
            'Auditor': Auditor.CATEGORY_AUDITOR,
            'Trainer': Auditor.CATEGORY_TRAINER,
        }
        
        model_category = category_mapping.get(category)
        if not model_category:
            self.stdout.write(
                self.style.ERROR(f'Unknown category: {category} for auditor: {auditor_name}')
            )
            return

        # Find or create auditor
        try:
            auditor, created = Auditor.objects.get_or_create(
                ime_prezime=auditor_name,
                defaults={
                    'kategorija': model_category,
                    'technical_area_code': ta_code,
                    'covers_all_standards': standard.upper() == 'SVI',
                    'email': f'{auditor_name.lower().replace(" ", ".")}@example.com',  # Placeholder
                    'telefon': '+381000000000',  # Placeholder
                }
            )
            
            if created:
                self.stdout.write(
                    self.style.SUCCESS(f'Created auditor: {auditor_name}')
                )
            else:
                # Update existing auditor
                auditor.technical_area_code = ta_code
                auditor.covers_all_standards = standard.upper() == 'SVI'
                if not dry_run:
                    auditor.save()
                self.stdout.write(
                    self.style.SUCCESS(f'Updated auditor: {auditor_name}')
                )

        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Error processing auditor {auditor_name}: {str(e)}')
            )
            return

        # Process EAC codes for Technical Experts
        if model_category == Auditor.CATEGORY_TECHNICAL_EXPERT and eac_codes:
            eac_list = [code.strip() for code in eac_codes.split(',') if code.strip()]
            
            for i, eac_code in enumerate(eac_list):
                try:
                    iaf_eac_obj = IAFEACCode.objects.get(iaf_code=eac_code)
                    
                    auditor_iaf, created = AuditorIAFEACCode.objects.get_or_create(
                        auditor=auditor,
                        iaf_eac_code=iaf_eac_obj,
                        defaults={
                            'is_primary': i == 0,  # First code is primary
                            'notes': f'TA: {ta_code}. {comment}' if comment else f'TA: {ta_code}'
                        }
                    )
                    
                    if created:
                        self.stdout.write(
                            self.style.SUCCESS(f'  Added IAF/EAC code {eac_code} to {auditor_name}')
                        )
                    else:
                        self.stdout.write(
                            self.style.WARNING(f'  IAF/EAC code {eac_code} already exists for {auditor_name}')
                        )
                        
                except IAFEACCode.DoesNotExist:
                    self.stdout.write(
                        self.style.ERROR(f'  IAF/EAC code {eac_code} not found in database')
                    )

        # Handle "SVI" standards assignment
        if standard.upper() == 'SVI' and not dry_run:
            try:
                auditor.assign_all_standards()
                self.stdout.write(
                    self.style.SUCCESS(f'  Assigned all standards to {auditor_name}')
                )
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f'  Error assigning standards to {auditor_name}: {str(e)}')
                )
