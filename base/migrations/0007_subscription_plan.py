# Generated by Django 4.1.6 on 2023-02-17 10:48

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0006_remove_stripecustomer_stripesubscriptionid_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='subscription',
            name='plan',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='base.package'),
        ),
    ]
