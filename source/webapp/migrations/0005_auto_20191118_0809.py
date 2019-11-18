# Generated by Django 2.1 on 2019-11-18 08:09

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('webapp', '0004_product_in_order'),
    ]

    operations = [
        migrations.AlterField(
            model_name='orderproduct',
            name='order',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='order_products', to='webapp.Order', verbose_name='Заказ'),
        ),
        migrations.AlterField(
            model_name='orderproduct',
            name='product',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='products_in_order', to='webapp.Product', verbose_name='Товар'),
        ),
    ]
