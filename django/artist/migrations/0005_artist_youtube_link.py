# Generated by Django 2.0.2 on 2018-02-27 11:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('youtube', '0001_initial'),
        ('artist', '0004_auto_20180227_1611'),
    ]

    operations = [
        migrations.AddField(
            model_name='artist',
            name='youtube_link',
            field=models.ManyToManyField(blank=True, to='youtube.Youtube'),
        ),
    ]