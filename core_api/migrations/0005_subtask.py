from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ('core_api', '0004_task_board_category_task_task_category'),
    ]

    operations = [
        migrations.CreateModel(
            name='Subtask',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=255)),
                ('completed', models.BooleanField(default=False)),
                ('parent_item', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='components', to='core_api.task')),
            ],
        ),
    ]