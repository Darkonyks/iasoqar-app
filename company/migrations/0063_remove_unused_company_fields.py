# Generated manually
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('company', '0062_alter_iafeaccode_description_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='company',
            name='initial_audit_conducted_date',
        ),
        migrations.RemoveField(
            model_name='company',
            name='visits_per_year',
        ),
        migrations.RemoveField(
            model_name='company',
            name='audit_days_each',
        ),
    ]
