# Generated by Django 2.0.2 on 2018-02-22 23:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('album', '0004_auto_20180223_0749'),
    ]

    operations = [
        migrations.AlterField(
            model_name='album',
            name='release_date',
            field=models.DateField(blank=True, null=True),
        ),
    ]