# Generated manually to expose the MenuItem.branches join table to ETL syncs.

import django.db.models.deletion
from django.db import migrations, models


def add_menu_item_branch_timestamps(apps, schema_editor):
    table_name = "menu_menuitem_branches"
    existing_columns = {
        column.name
        for column in schema_editor.connection.introspection.get_table_description(
            schema_editor.connection.cursor(),
            table_name,
        )
    }

    if schema_editor.connection.vendor == "postgresql":
        if "created_at" not in existing_columns:
            schema_editor.execute(
                f'ALTER TABLE "{table_name}" '
                "ADD COLUMN created_at timestamp with time zone "
                "NOT NULL DEFAULT CURRENT_TIMESTAMP"
            )
        if "updated_at" not in existing_columns:
            schema_editor.execute(
                f'ALTER TABLE "{table_name}" '
                "ADD COLUMN updated_at timestamp with time zone "
                "NOT NULL DEFAULT CURRENT_TIMESTAMP"
            )
        schema_editor.execute(
            f'CREATE INDEX IF NOT EXISTS "{table_name}_updated_at_idx" '
            f'ON "{table_name}" ("updated_at")'
        )
        return

    if "created_at" not in existing_columns:
        schema_editor.execute(
            f'ALTER TABLE "{table_name}" ADD COLUMN created_at datetime'
        )
    if "updated_at" not in existing_columns:
        schema_editor.execute(
            f'ALTER TABLE "{table_name}" ADD COLUMN updated_at datetime'
        )


def remove_menu_item_branch_timestamps(apps, schema_editor):
    table_name = "menu_menuitem_branches"

    if schema_editor.connection.vendor == "postgresql":
        schema_editor.execute(
            f'DROP INDEX IF EXISTS "{table_name}_updated_at_idx"'
        )
        schema_editor.execute(
            f'ALTER TABLE "{table_name}" DROP COLUMN IF EXISTS updated_at'
        )
        schema_editor.execute(
            f'ALTER TABLE "{table_name}" DROP COLUMN IF EXISTS created_at'
        )


class Migration(migrations.Migration):

    dependencies = [
        ('menu', '0010_add_etl_timestamps'),
    ]

    operations = [
        migrations.SeparateDatabaseAndState(
            database_operations=[
                migrations.RunPython(
                    add_menu_item_branch_timestamps,
                    remove_menu_item_branch_timestamps,
                ),
            ],
            state_operations=[
                migrations.CreateModel(
                    name='MenuItemBranch',
                    fields=[
                        ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                        ('created_at', models.DateTimeField(auto_now_add=True)),
                        ('updated_at', models.DateTimeField(auto_now=True, db_index=True)),
                        ('branch', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='menu.branch')),
                        ('menu_item', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='menu.menuitem')),
                    ],
                    options={
                        'db_table': 'menu_menuitem_branches',
                        'ordering': ['id'],
                        'constraints': [
                            models.UniqueConstraint(fields=('menu_item', 'branch'), name='unique_menu_item_branch'),
                        ],
                    },
                ),
                migrations.AlterField(
                    model_name='menuitem',
                    name='branches',
                    field=models.ManyToManyField(blank=True, related_name='menu_items', through='menu.MenuItemBranch', to='menu.branch'),
                ),
            ],
        ),
    ]
