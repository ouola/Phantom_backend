# Generated by Django 5.0.7 on 2024-08-28 10:11

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Pharmacy',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255, unique=True)),
                ('cash_balance', models.DecimalField(decimal_places=2, max_digits=10)),
                ('opening_hours', models.TextField()),
            ],
        ),
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('cash_balance', models.DecimalField(decimal_places=2, max_digits=10)),
            ],
        ),
        migrations.CreateModel(
            name='Mask',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('price', models.DecimalField(decimal_places=2, max_digits=10)),
                ('pharmacy', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='masks', to='phantom_app.pharmacy')),
            ],
        ),
        migrations.CreateModel(
            name='PurchaseHistory',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('mask_name', models.CharField(max_length=255)),
                ('transaction_amount', models.DecimalField(decimal_places=2, max_digits=10)),
                ('transaction_date', models.DateTimeField()),
                ('pharmacy', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='purchases', to='phantom_app.pharmacy')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='purchases', to='phantom_app.user')),
            ],
        ),
    ]
