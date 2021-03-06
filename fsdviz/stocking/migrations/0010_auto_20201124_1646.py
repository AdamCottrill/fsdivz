# Generated by Django 2.2 on 2020-11-24 21:46

from django.db import migrations, models
import fsdviz.stocking.models


class Migration(migrations.Migration):

    dependencies = [
        ('stocking', '0009_auto_20201116_1356'),
    ]

    operations = [
        migrations.AlterField(
            model_name='stockingevent',
            name='stock_id',
            field=models.CharField(db_index=True, default=fsdviz.stocking.models.unique_string, max_length=100, unique=True, verbose_name='unique event identifier provided by agency'),
        ),
    ]
