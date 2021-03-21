# Generated by Django 2.1.5 on 2019-04-04 18:10

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0003_auto_20190404_1756'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='user',
            name='program',
        ),
        migrations.AddField(
            model_name='user',
            name='program',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='main.ProgramInfo'),
        ),
    ]