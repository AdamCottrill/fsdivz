# Generated by Django 2.2.19 on 2021-05-10 15:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('stocking', '0014_added_yearling_equivalents'),
    ]

    operations = [
        migrations.AlterField(
            model_name='yearlingequivalent',
            name='comment',
            field=models.CharField(blank=True, max_length=1000, null=True),
        ),
    ]
