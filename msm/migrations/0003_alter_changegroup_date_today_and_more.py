# Generated by Django 4.0.5 on 2022-10-17 15:22

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('msm', '0002_alter_changegroup_date_today_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='changegroup',
            name='date_today',
            field=models.DateField(blank=True, default=datetime.date(2022, 10, 17), null=True),
        ),
        migrations.AlterField(
            model_name='checkintable',
            name='date_today',
            field=models.DateField(blank=True, default=datetime.date(2022, 10, 17), null=True),
        ),
        migrations.AlterField(
            model_name='externalwork',
            name='ex_work_date',
            field=models.DateField(blank=True, default=datetime.date(2022, 10, 17), null=True),
        ),
        migrations.AlterField(
            model_name='userprofile',
            name='contract_type',
            field=models.SmallIntegerField(blank=True, choices=[(1, 'CDI'), (2, 'CDD'), (3, 'Temporary'), (4, 'Trial')], default=3, null=True, verbose_name='Level'),
        ),
    ]
