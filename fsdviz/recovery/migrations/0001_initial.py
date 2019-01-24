# Generated by Django 2.1.4 on 2019-01-24 20:13

import django.contrib.gis.db.models.fields
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('common', '0010_remove_cwt_agency'),
    ]

    operations = [
        migrations.CreateModel(
            name='Recovery',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('cwt_number', models.CharField(db_index=True, max_length=6)),
                ('manufacturer', models.CharField(choices=[('mm', 'Micro Mark'), ('nmt', 'Northwest Marine Technology')], default='nmt', max_length=3)),
                ('sequential_number', models.IntegerField(default=1)),
                ('fish_identifier_key', models.CharField(max_length=80)),
                ('mesh_size', models.FloatField(blank=True, null=True)),
                ('length', models.IntegerField(blank=True, null=True)),
                ('weight', models.IntegerField(blank=True, null=True)),
                ('age', models.IntegerField(blank=True, null=True)),
                ('agestructure', models.CharField(blank=True, max_length=20, null=True)),
                ('sex', models.CharField(choices=[('M', 'Male'), ('F', 'Female'), ('U', 'Unknown')], default='U', max_length=1)),
                ('maturity', models.CharField(choices=[('I', 'Immature'), ('M', 'Mature'), ('U', 'Unknown'), ('G', 'Gravid'), ('S', 'Spent'), ('R', 'Ripe')], default='U', max_length=1)),
                ('clipc', models.CharField(blank=True, db_index=True, max_length=15, null=True)),
                ('mark', models.CharField(blank=True, db_index=True, max_length=15, null=True)),
                ('A1A2A3', models.IntegerField(blank=True, null=True)),
                ('A1', models.IntegerField(blank=True, null=True)),
                ('A2', models.IntegerField(blank=True, null=True)),
                ('A3', models.IntegerField(blank=True, null=True)),
                ('A4', models.IntegerField(blank=True, null=True)),
                ('B1', models.IntegerField(blank=True, null=True)),
                ('B2', models.IntegerField(blank=True, null=True)),
                ('B3', models.IntegerField(blank=True, null=True)),
                ('B4', models.IntegerField(blank=True, null=True)),
                ('comment', models.CharField(blank=True, max_length=500, null=True)),
                ('tagid', models.CharField(blank=True, max_length=20, null=True)),
                ('tagdoc', models.CharField(blank=True, max_length=20, null=True)),
            ],
            options={
                'ordering': ['-recovery_event__year', 'recovery_event__agengy__abbrev', 'fish_identifier_key'],
            },
        ),
        migrations.CreateModel(
            name='RecoveryEvent',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('lift_identifier', models.CharField(max_length=100, unique=True)),
                ('date', models.DateField(blank=True, null=True, verbose_name='Stocking event date')),
                ('day', models.IntegerField(blank=True, null=True, verbose_name='Day of the month')),
                ('month', models.IntegerField(blank=True, db_index=True, null=True, verbose_name='Month of recovery event as an integer')),
                ('year', models.IntegerField(db_index=True, verbose_name='year of the recovery event as an integer >1900')),
                ('location', models.CharField(blank=True, max_length=100, null=True)),
                ('dd_lat', models.FloatField(blank=True, null=True, verbose_name='Latitude in decimal degrees')),
                ('dd_lon', models.FloatField(blank=True, null=True, verbose_name='Longitude in decimal degrees')),
                ('geom', django.contrib.gis.db.models.fields.PointField(blank=True, null=True, srid=4326, verbose_name='GeoDjango spatial point field')),
                ('grid_5', models.CharField(blank=True, max_length=4, null=True)),
                ('program_type', models.CharField(blank=True, max_length=100, null=True)),
                ('program_description', models.CharField(blank=True, max_length=100, null=True)),
                ('gear', models.CharField(blank=True, max_length=100, null=True)),
                ('nights', models.IntegerField(blank=True, null=True)),
                ('net_length', models.FloatField(blank=True, null=True)),
                ('depth_min', models.FloatField(blank=True, null=True)),
                ('depth_max', models.FloatField(blank=True, null=True)),
                ('depth_avg', models.FloatField(blank=True, null=True)),
                ('surface_temp', models.FloatField(blank=True, null=True)),
                ('bottom_temp', models.FloatField(blank=True, null=True)),
                ('net_material', models.CharField(blank=True, choices=[('M', 'Monofilament'), ('N', 'Nylon')], max_length=2, null=True)),
                ('mesh_min', models.FloatField(blank=True, null=True)),
                ('mesh_max', models.FloatField(blank=True, null=True)),
                ('comments', models.CharField(blank=True, max_length=500, null=True)),
                ('agency', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='recovery_events', to='common.Agency')),
                ('grid_10', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='recovery_events', to='common.Grid10')),
                ('lake', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='recovery_events', to='common.Lake')),
                ('latlong_flag', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='recovery_events', to='common.LatLonFlag')),
                ('stateprov', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='recovery_events', to='common.StateProvince')),
            ],
            options={
                'ordering': ['-year', 'agency', 'lift_identifier'],
            },
        ),
        migrations.AddField(
            model_name='recovery',
            name='recovery_event',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='recovered_tags', to='recovery.RecoveryEvent'),
        ),
        migrations.AddField(
            model_name='recovery',
            name='species',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='recovered_tag', to='common.Species'),
        ),
        migrations.AlterUniqueTogether(
            name='recovery',
            unique_together={('recovery_event', 'fish_identifier_key')},
        ),
    ]
