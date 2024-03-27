# Generated by Django 5.0.1 on 2024-01-28 17:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0003_customuser_is_superuser'),
    ]

    operations = [
        migrations.RenameField(
            model_name='customuser',
            old_name='is_superuser',
            new_name='is_admin',
        ),
        migrations.AddField(
            model_name='customuser',
            name='is_active',
            field=models.BooleanField(default=True),
        ),
    ]