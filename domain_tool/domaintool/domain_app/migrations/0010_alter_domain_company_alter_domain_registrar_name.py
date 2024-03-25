# Generated by Django 4.2.7 on 2024-02-10 08:53

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('domain_app', '0009_domain_registrar_name'),
    ]

    operations = [
        migrations.AlterField(
            model_name='domain',
            name='company',
            field=models.ForeignKey(blank=True, on_delete=django.db.models.deletion.CASCADE, to='domain_app.company'),
        ),
        migrations.AlterField(
            model_name='domain',
            name='registrar_name',
            field=models.CharField(blank=True, max_length=300, null=True),
        ),
    ]
