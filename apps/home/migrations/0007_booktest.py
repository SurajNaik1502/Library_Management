# Generated by Django 3.2.6 on 2024-10-06 01:55

from django.db import migrations, models
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0006_alter_bookcheckout_book_id'),
    ]

    operations = [
        migrations.CreateModel(
            name='BookTest',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('book_id', models.UUIDField(default=uuid.uuid4, editable=False, unique=True)),
                ('title', models.CharField(max_length=255)),
                ('category', models.CharField(max_length=100)),
                ('description', models.TextField(blank=True, null=True)),
                ('barcode', models.CharField(max_length=50, unique=True)),
                ('location', models.IntegerField(default=0)),
            ],
        ),
    ]