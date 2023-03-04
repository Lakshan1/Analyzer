# Generated by Django 4.1.6 on 2023-02-11 10:48

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Live_Counts',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('user', models.IntegerField(default=0)),
                ('desktop', models.IntegerField(default=0)),
                ('mobile', models.IntegerField(default=0)),
                ('app', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='base.app')),
                ('ip_addresses', models.ManyToManyField(blank=True, null=True, to='base.ip')),
                ('locations', models.ManyToManyField(blank=True, null=True, to='base.locations')),
            ],
        ),
    ]