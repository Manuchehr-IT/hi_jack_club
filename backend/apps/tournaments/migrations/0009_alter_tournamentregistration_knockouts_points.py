from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tournaments', '0008_tournament_olap_report_completed_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='tournamentregistration',
            name='knockouts',
            field=models.IntegerField(default=0, verbose_name='Нокауты'),
        ),
        migrations.AlterField(
            model_name='tournamentregistration',
            name='points',
            field=models.IntegerField(default=0, verbose_name='Очки рейтинга'),
        ),
    ]
