# Generated by Django 2.2 on 2019-04-19 00:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('common', '0002_auto_20190413_2002'),
    ]

    operations = [
        migrations.AddField(
            model_name='grid10',
            name='slug',
            field=models.SlugField(default='slug', editable=False),
            preserve_default=False,
        ),
    ]