# Generated by Django 5.0 on 2025-01-19 09:13

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('system', '0025_transaction_transactionhistory'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='transactionhistory',
            name='transaction',
        ),
        migrations.DeleteModel(
            name='Transaction',
        ),
        migrations.DeleteModel(
            name='TransactionHistory',
        ),
    ]
