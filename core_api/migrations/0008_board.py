from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('core_api', '0007_task_icon'),
    ]

    operations = [
        migrations.CreateModel(
            name='Board',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255, unique=True)),
            ],
        ),
    ]