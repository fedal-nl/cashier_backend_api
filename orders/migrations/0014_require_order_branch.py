# Generated manually to require branches on orders.

from django.db import migrations, models
import django.db.models.deletion


def set_missing_order_branches(apps, schema_editor):
    Branch = apps.get_model("menu", "Branch")
    Order = apps.get_model("orders", "Order")

    first_branch = Branch.objects.order_by("id").first()
    if first_branch is None:
        if Order.objects.filter(branch__isnull=True).exists():
            raise RuntimeError(
                "Cannot assign missing order branches because no branches exist."
            )
        return

    Order.objects.filter(branch__isnull=True).update(branch=first_branch)


class Migration(migrations.Migration):
    dependencies = [
        ("menu", "0009_branch_menuitem_branches"),
        ("orders", "0013_order_type_and_nullable_customer"),
    ]

    operations = [
        migrations.RunPython(
            set_missing_order_branches,
            migrations.RunPython.noop,
        ),
        migrations.AlterField(
            model_name="order",
            name="branch",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.PROTECT,
                related_name="orders",
                to="menu.branch",
            ),
        ),
    ]
