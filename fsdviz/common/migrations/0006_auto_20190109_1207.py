# Generated by Django 2.1.4 on 2019-01-09 17:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('common', '0005_auto_20190109_1114'),
    ]

    operations = [
        migrations.AlterField(
            model_name='cwt',
            name='multiple_agencies',
            field=models.BooleanField(db_index=True, default=False, verbose_name='True if this cwt has been stocked by more than one agency'),
        ),
        migrations.AlterField(
            model_name='cwt',
            name='multiple_grid10s',
            field=models.BooleanField(db_index=True, default=False, verbose_name='True if this cwt has been stocked by more than one 10-minute grid'),
        ),
        migrations.AlterField(
            model_name='cwt',
            name='multiple_lakes',
            field=models.BooleanField(db_index=True, default=False, verbose_name='True if this cwt has been stocked in more than one lake'),
        ),
        migrations.AlterField(
            model_name='cwt',
            name='multiple_makers',
            field=models.BooleanField(db_index=True, default=False, verbose_name='True if this cwt has been made by more than one tag manufacturer'),
        ),
        migrations.AlterField(
            model_name='cwt',
            name='multiple_species',
            field=models.BooleanField(db_index=True, default=False, verbose_name='True if this cwt has been stocked in more than one species'),
        ),
        migrations.AlterField(
            model_name='cwt',
            name='multiple_strains',
            field=models.BooleanField(db_index=True, default=False, verbose_name='True if this cwt has been stocked in more than one strain'),
        ),
        migrations.AlterField(
            model_name='cwt',
            name='multiple_yearclasses',
            field=models.BooleanField(db_index=True, default=False, verbose_name='True if this cwt has been stocked in more than one year class'),
        ),
        migrations.AlterField(
            model_name='cwt',
            name='tag_reused',
            field=models.BooleanField(db_index=True, default=False, verbose_name='True if this cwt has been stocked by more than one species, strain, or yearclass'),
        ),
    ]
