from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('core_api', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='task',
            name='board',
        ),
        migrations.RemoveField(
            model_name='task',
            name='contacts',
        ),
        migrations.RemoveField(
            model_name='task',
            name='category',
        ),
        migrations.AlterField(
            model_name='task',
            name='priority',
            field=models.CharField(
                choices=[
                    ('low', 'Low'), 
                    ('medium', 'Medium'), 
                    ('urgent', 'Urgent')
                ], 
                max_length=10
            ),
        ),
        migrations.AlterField(
            model_name='task',
            name='status',
            field=models.CharField(
                choices=[
                    ('to-do', 'To Do'), 
                    ('in-progress', 'In Progress'), 
                    ('await-feedback', 'Await Feedback'), 
                    ('done', 'Done')
                ], 
                default='to-do', 
                max_length=20
            ),
        ),
        migrations.DeleteModel(
            name='Board',
        ),
        migrations.DeleteModel(
            name='Contact',
        ),
    ]