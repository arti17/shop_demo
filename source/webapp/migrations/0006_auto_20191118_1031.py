# Generated by Django 2.1 on 2019-11-18 10:31

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('webapp', '0005_auto_20191118_0809'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='order',
            options={'permissions': [('can_deliver_order', 'Может доставлять заказ'), ('can_cancel_order', 'Может отменять заказ')], 'verbose_name': 'Заказ', 'verbose_name_plural': 'Заказы'},
        ),
    ]
