# Generated manually after allowing duplicate customer contact details.

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("orders", "0014_require_order_branch"),
    ]

    operations = [
        migrations.AlterField(
            model_name="customer",
            name="email",
            field=models.EmailField(
                blank=True,
                max_length=254,
                null=True,
                verbose_name="البريد الإلكتروني",
            ),
        ),
        migrations.AlterField(
            model_name="customer",
            name="phone_number",
            field=models.CharField(
                blank=True,
                max_length=20,
                null=True,
                verbose_name="رقم الهاتف",
            ),
        ),
    ]
