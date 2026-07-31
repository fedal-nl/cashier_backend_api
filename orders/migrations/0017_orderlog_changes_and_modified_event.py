from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("orders", "0016_customer_phone_trigram_index"),
    ]

    operations = [
        migrations.AddField(
            model_name="orderlog",
            name="changes",
            field=models.JSONField(blank=True, default=dict),
        ),
        migrations.AlterField(
            model_name="orderlog",
            name="event_type",
            field=models.CharField(
                choices=[
                    ("created", "Created"),
                    ("status_updated", "Status updated"),
                    ("modified", "Modified"),
                ],
                max_length=20,
            ),
        ),
    ]
