import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core_api', '0008_board'),
    ]

    operations = [
        migrations.CreateModel(
            name='ProjectSpace',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255, unique=True)),
            ],
        ),
        migrations.CreateModel(
            name='TeamMember',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('email', models.EmailField(max_length=254, unique=True)),
                ('phone', models.CharField(max_length=20)),
                ('color', models.CharField(default='#000000', max_length=7)),
            ],
        ),
        migrations.CreateModel(
            name='WorkItem',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=255)),
                ('description', models.TextField(blank=True, null=True)),
                ('due_date', models.DateField()),
                ('priority', models.CharField(choices=[('low', 'Low'), ('medium', 'Medium'), ('urgent', 'Urgent')], max_length=10)),
                ('status', models.CharField(choices=[('to-do', 'To Do'), ('in-progress', 'In Progress'), ('await-feedback', 'Await Feedback'), ('done', 'Done')], default='to-do', max_length=20)),
                ('task_category', models.CharField(blank=True, choices=[('Technical Task', 'Technical Task'), ('User Story', 'User Story')], max_length=20, null=True)),
                ('board_category', models.CharField(choices=[('to-do', 'To Do'), ('in-progress', 'In Progress'), ('await-feedback', 'Await Feedback'), ('done', 'Done')], default='to-do', max_length=20)),
                ('icon', models.CharField(blank=True, default='/static/default.svg', max_length=255, null=True)),
                ('contacts', models.ManyToManyField(related_name='assignments', to='core_api.teammember')),
            ],
        ),
        migrations.CreateModel(
            name='WorkItemComponent',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=255)),
                ('completed', models.BooleanField(default=False)),
                ('parent_item', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='components', to='core_api.workitem')),
            ],
        ),
        migrations.DeleteModel(
            name='Board',
        ),
        migrations.RemoveField(
            model_name='task',
            name='contacts',
        ),
        migrations.RemoveField(
            model_name='subtask',
            name='parent_item',
        ),
        migrations.DeleteModel(
            name='Contact',
        ),
        migrations.DeleteModel(
            name='Subtask',
        ),
        migrations.DeleteModel(
            name='Task',
        ),
    ]