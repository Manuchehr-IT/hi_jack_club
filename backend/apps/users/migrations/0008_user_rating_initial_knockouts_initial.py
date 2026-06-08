from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0007_user_referral_code_user_referrer'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='rating_initial',
            field=models.IntegerField(default=0, verbose_name='Рейтинг (базовый)'),
        ),
        migrations.AddField(
            model_name='user',
            name='knockouts_initial',
            field=models.IntegerField(default=0, verbose_name='Нокауты (базовые)'),
        ),
    ]
