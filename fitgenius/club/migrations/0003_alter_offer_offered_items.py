# Generated by Django 3.2.13 on 2022-04-24 16:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('club', '0002_auto_20220424_1143'),
    ]

    operations = [
        migrations.AlterField(
            model_name='offer',
            name='offered_items',
            field=models.ManyToManyField(related_name='offfers', to='club.OfferedItem'),
        ),
    ]
