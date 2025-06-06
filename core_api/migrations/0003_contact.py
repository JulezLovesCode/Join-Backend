from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('core_api', '0002_remove_task_board_remove_task_contacts_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='Contact',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('email', models.EmailField(max_length=254, unique=True)),
                ('phone', models.CharField(max_length=20)),
                ('color', models.CharField(default='#000000', max_length=7)),
            ],
        ),
    ]