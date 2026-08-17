from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("menu", "0012_category_rankings"),
        ("orders", "0017_orderlog_changes_and_modified_event"),
    ]

    operations = [
        migrations.CreateModel(
            name="Campaign",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("campaign_name", models.CharField(db_index=True, max_length=255)),
                ("start_date", models.DateField(db_index=True)),
                ("end_date", models.DateField(db_index=True)),
                (
                    "channel",
                    models.CharField(
                        choices=[
                            ("tiktok", "TikTok"),
                            ("instagram", "Instagram"),
                            ("online", "Online"),
                        ],
                        max_length=20,
                    ),
                ),
                ("amount_spent", models.DecimalField(decimal_places=2, max_digits=12)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True, db_index=True)),
                (
                    "menu_items",
                    models.ManyToManyField(
                        related_name="campaigns", to="menu.menuitem"
                    ),
                ),
            ],
            options={"ordering": ["-start_date", "-id"]},
        ),
    ]
