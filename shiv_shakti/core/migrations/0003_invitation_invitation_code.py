# Generated by Django 5.0.7 on 2024-08-09 09:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0002_invitationcode'),
    ]

    operations = [
        migrations.AddField(
            model_name='invitation',
            name='invitation_code',
            field=models.CharField(blank=True, default='', max_length=255, unique=True),
        ),
    ]
