# Generated by Django 5.2.1 on 2025-05-26 21:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('libros', '0002_alter_author_email'),
    ]

    operations = [
        migrations.AddField(
            model_name='book',
            name='download_url',
            field=models.URLField(blank=True, help_text='URL para descargar el libro (ej: https://ejemplo.com/libro.pdf)', null=True, verbose_name='Enlace de descarga'),
        ),
    ]
