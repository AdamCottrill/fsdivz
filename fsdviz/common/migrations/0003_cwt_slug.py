# Generated by Django 2.2 on 2019-09-23 20:09

from django.db import migrations, models


class Migration(migrations.Migration):
    def forwards_func(apps, schema_editor):
        CWT = apps.get_model("common", "CWT")
        for instance in CWT.objects.all():
            if not instance.slug:
                instance.slug = "{}_{}".format(
                    instance.cwt_number, instance.manufacturer
                )
                instance.save()

    def reverse_func(apps, schema_editor):
        pass

    dependencies = [("common", "0002_auto_20190812_0954")]

    operations = [
        migrations.AddField(
            model_name="cwt",
            name="slug",
            field=models.CharField(max_length=10, null=True, unique=True),
        ),
        migrations.RunPython(forwards_func, reverse_func),
    ]