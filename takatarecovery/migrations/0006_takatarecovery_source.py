# Generated by Django 2.1.10 on 2019-09-25 04:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('takatarecovery', '0005_auto_20190919_1108'),
    ]

    operations = [
        migrations.AddField(
            model_name='takatarecovery',
            name='source',
            field=models.CharField(max_length=10, null=True),
        ),
    ]
