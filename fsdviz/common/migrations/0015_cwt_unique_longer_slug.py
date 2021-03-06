# Generated by Django 2.2 on 2020-08-06 17:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('common', '0014_added_FinClip_and_m2m_to_event'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='finclip',
            options={'ordering': ['abbrev']},
        ),
        migrations.AlterField(
            model_name='cwt',
            name='slug',
            field=models.CharField(max_length=30, unique=True),
        ),
        migrations.AlterField(
            model_name='fishtag',
            name='tag_colour',
            field=models.CharField(choices=[('unknown', 'Unknown'), ('white', 'White'), ('red', 'Red'), ('orange', 'Orange'), ('purple', 'Purple'), ('yellow', 'Yellow'), ('green', 'Green'), ('blue', 'Blue')], max_length=10),
        ),
        migrations.AlterUniqueTogether(
            name='cwt',
            unique_together={('cwt_number', 'manufacturer', 'tag_type')},
        ),
    ]
