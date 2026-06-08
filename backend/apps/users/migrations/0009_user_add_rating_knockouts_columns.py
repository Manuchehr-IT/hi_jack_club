from django.db import migrations


class Migration(migrations.Migration):
    """
    Adds rating and knockouts columns that exist in 0001_initial on dev
    but were missing on databases migrated from main branch.
    Uses IF NOT EXISTS so it's safe to run on both environments.
    """

    dependencies = [
        ('users', '0008_user_rating_initial_knockouts_initial'),
    ]

    operations = [
        migrations.RunSQL(
            sql=[
                "ALTER TABLE users_user ADD COLUMN IF NOT EXISTS rating INTEGER NOT NULL DEFAULT 0;",
                "ALTER TABLE users_user ADD COLUMN IF NOT EXISTS knockouts INTEGER NOT NULL DEFAULT 0;",
            ],
            reverse_sql=[
                "ALTER TABLE users_user DROP COLUMN IF EXISTS rating;",
                "ALTER TABLE users_user DROP COLUMN IF EXISTS knockouts;",
            ],
        ),
    ]
