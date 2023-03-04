# Generated by Django 4.1.6 on 2023-03-03 05:08

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0009_alter_paymenthistory_user'),
    ]

    operations = [
        migrations.CreateModel(
            name='Counts',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateTimeField()),
                ('user', models.IntegerField(default=0)),
                ('desktop', models.IntegerField(default=0)),
                ('mobile', models.IntegerField(default=0)),
                ('app', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='base.app')),
            ],
        ),
    ]