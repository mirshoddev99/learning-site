# Generated by Django 4.1.1 on 2023-02-20 06:51

from django.conf import settings
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('courses', '0002_vide_text_image_file_content'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='Vide',
            new_name='Video',
        ),
    ]