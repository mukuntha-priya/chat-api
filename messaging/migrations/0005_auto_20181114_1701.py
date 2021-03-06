# Generated by Django 2.1.3 on 2018-11-14 17:01

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('messaging', '0004_auto_20181111_1348'),
    ]

    operations = [
        migrations.AlterField(
            model_name='directmessagehistory',
            name='last_seen_message',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='messaging.Message'),
        ),
        migrations.AlterField(
            model_name='grouphistory',
            name='last_seen_message',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='messaging.Message'),
        ),
    ]
