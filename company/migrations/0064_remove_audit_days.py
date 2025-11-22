# Generated manually
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('company', '0063_remove_unused_company_fields'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='company',
            name='audit_days',
        ),
    ]
