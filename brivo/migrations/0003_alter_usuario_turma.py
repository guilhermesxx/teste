# Generated by Django 5.2 on 2025-05-27 22:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('brivo', '0002_rename_is_admin_usuario_is_staff_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='usuario',
            name='turma',
            field=models.CharField(blank=True, max_length=10, null=True),
        ),
    ]
