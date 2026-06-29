# Generated manually for order type support.

from django.db import migrations, models
import django.db.models.deletion


def set_delivery_company_one_orders_to_dine_in(apps, schema_editor):
    Order = apps.get_model("orders", "Order")
    Order.objects.filter(delivery_company_id=1).update(order_type="dine_in")


def set_delivery_company_one_orders_to_delivery(apps, schema_editor):
    Order = apps.get_model("orders", "Order")
    Order.objects.filter(delivery_company_id=1, order_type="dine_in").update(
        order_type="delivery"
    )


class Migration(migrations.Migration):
    dependencies = [
        ("orders", "0012_add_etl_timestamps"),
    ]

    operations = [
        migrations.AddField(
            model_name="order",
            name="order_type",
            field=models.CharField(
                choices=[
                    ("delivery", "توصيل"),
                    ("takeaway", "استلام خارجي"),
                    ("dine_in", "داخل المطعم"),
                ],
                default="delivery",
                max_length=20,
            ),
        ),
        migrations.AlterField(
            model_name="order",
            name="customer",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="orders",
                to="orders.customer",
            ),
        ),
        migrations.AlterField(
            model_name="orderlog",
            name="customer",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="order_logs",
                to="orders.customer",
            ),
        ),
        migrations.RunPython(
            set_delivery_company_one_orders_to_dine_in,
            set_delivery_company_one_orders_to_delivery,
        ),
    ]
