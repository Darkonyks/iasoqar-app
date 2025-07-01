from django.db import migrations

class Migration(migrations.Migration):

    dependencies = [
        ('company', '0031_alter_certificationcycle_end_date'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='calendarevent',
            name='naredne_provere',
        ),
        migrations.DeleteModel(
            name='NaredneProvere',
        ),
    ]
