from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('core_api', '0006_task_contacts'),
    ]

    operations = [
        migrations.AddField(
            model_name='task',
            name='icon',
            field=models.CharField(blank=True, default='/static/default.svg', max_length=255, null=True),
        ),
    ]