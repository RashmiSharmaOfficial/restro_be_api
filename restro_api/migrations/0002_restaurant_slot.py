# Generated by Django 5.1.3 on 2024-12-01 19:10

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('restro_api', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Restaurant',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('city', models.CharField(max_length=100)),
                ('area', models.CharField(max_length=100)),
                ('cuisine', models.CharField(max_length=255)),
                ('rating', models.DecimalField(decimal_places=1, default=0.0, max_digits=2)),
                ('cost_for_two', models.DecimalField(decimal_places=2, max_digits=10)),
                ('is_veg', models.BooleanField(default=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('owner', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='restro_api.user')),
            ],
        ),
        migrations.CreateModel(
            name='Slot',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateField()),
                ('time', models.TimeField()),
                ('capacity', models.IntegerField()),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('restaurant', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='restro_api.restaurant')),
            ],
        ),
    ]
