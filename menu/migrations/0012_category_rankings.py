from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("menu", "0011_menuitembranch_timestamps"),
    ]

    operations = [
        migrations.AddField(
            model_name="category",
            name="admin_ranking",
            field=models.PositiveIntegerField(default=0),
        ),
        migrations.AddField(
            model_name="category",
            name="frontend_ranking",
            field=models.PositiveIntegerField(default=0),
        ),
        migrations.AlterModelOptions(
            name="category",
            options={
                "ordering": ["frontend_ranking", "name_ar", "id"],
                "verbose_name_plural": "Categories",
            },
        ),
    ]
