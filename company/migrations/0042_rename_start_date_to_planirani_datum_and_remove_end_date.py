from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("company", "0041_alter_cycleaudit_audit_status_and_more"),
    ]

    operations = [
        migrations.RenameField(
            model_name="certificationcycle",
            old_name="start_date",
            new_name="planirani_datum",
        ),
        migrations.RemoveField(
            model_name="certificationcycle",
            name="end_date",
        ),
    ]
