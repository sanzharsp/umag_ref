# Generated by Django 4.2 on 2024-07-18 12:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='responsetimecreate',
            name='content_type',
        ),
        migrations.RemoveField(
            model_name='responsetimecreate',
            name='object_id',
        ),
        migrations.RemoveField(
            model_name='responsetimedelete',
            name='content_type',
        ),
        migrations.RemoveField(
            model_name='responsetimedelete',
            name='object_id',
        ),
        migrations.AddField(
            model_name='supportbug',
            name='leads_id',
            field=models.CharField(blank=True, max_length=255, null=True, verbose_name='Идентификатор сделки'),
        ),
        migrations.AddField(
            model_name='supportconsultation',
            name='leads_id',
            field=models.CharField(blank=True, max_length=255, null=True, verbose_name='Идентификатор сделки'),
        ),
        migrations.AddField(
            model_name='supportgetcourse',
            name='leads_id',
            field=models.CharField(blank=True, max_length=255, null=True, verbose_name='Идентификатор сделки'),
        ),
        migrations.AddField(
            model_name='supportsynchronization',
            name='leads_id',
            field=models.CharField(blank=True, max_length=255, null=True, verbose_name='Идентификатор сделки'),
        ),
    ]