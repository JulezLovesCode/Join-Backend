from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('core_api', '0005_subtask'),
    ]

    operations = [
        migrations.AddField(
            model_name='task',
            name='contacts',
            field=models.ManyToManyField(related_name='assignments', to='core_api.contact'),
        ),
    ]