# Generated by Django 2.1 on 2019-09-02 22:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('twt_coop', '0002_auto_20190705_1752'),
    ]

    operations = [
        migrations.AddField(
            model_name='oauthtokentemp',
            name='user_id',
            field=models.CharField(db_index=True, max_length=30, null=True),
        ),
    ]
