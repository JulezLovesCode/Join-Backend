from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('core_api', '0003_contact'),
    ]

    operations = [
        migrations.AddField(
            model_name='task',
            name='board_category',
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
        migrations.AddField(
            model_name='task',
            name='task_category',
            field=models.CharField(
                blank=True, 
                choices=[
                    ('Technical Task', 'Technical Task'), 
                    ('User Story', 'User Story')
                ], 
                max_length=20, 
                null=True
            ),
        ),
    ]