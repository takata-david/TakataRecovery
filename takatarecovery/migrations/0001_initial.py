# Generated by Django 2.1.10 on 2019-09-16 05:15

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='takatarecovery',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('vin', models.CharField(max_length=50, null=True)),
                ('business_name', models.TextField(null=True)),
                ('contact_no', models.CharField(max_length=15, null=True)),
                ('date', models.DateField(null=True)),
            ],
        ),
    ]
