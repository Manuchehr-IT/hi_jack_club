from django.db import migrations


class Migration(migrations.Migration):
    """
    Drops rankings_calculated column that existed in main branch
    but was removed from the model in dev.
    Uses IF EXISTS so it's safe to run on both environments.
    """

    dependencies = [
        ('tournaments', '0009_alter_tournamentregistration_knockouts_points'),
    ]

    operations = [
        migrations.RunSQL(
            sql="ALTER TABLE tournaments_tournamentregistration DROP COLUMN IF EXISTS rankings_calculated;",
            reverse_sql=migrations.RunSQL.noop,
        ),
    ]
