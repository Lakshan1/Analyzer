# Generated by Django 4.1.6 on 2023-03-03 05:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0010_counts'),
    ]

    operations = [
        migrations.AlterField(
            model_name='counts',
            name='date',
            field=models.DateField(),
        ),
    ]
