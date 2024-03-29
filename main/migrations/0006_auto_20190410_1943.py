# Generated by Django 2.1.5 on 2019-04-10 19:43

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0005_auto_20190405_1150'),
    ]

    operations = [
        migrations.CreateModel(
            name='AdmittedUser',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
            ],
            options={
                'verbose_name': 'Допущенный пользователь',
                'verbose_name_plural': 'Допущенные пользователи',
            },
        ),
        migrations.CreateModel(
            name='AllowedProgram',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
            ],
            options={
                'verbose_name': 'Разрешенныая программа',
                'verbose_name_plural': 'Разрешенные программы',
            },
        ),
        migrations.RemoveField(
            model_name='programinfo',
            name='user',
        ),
        migrations.RemoveField(
            model_name='user',
            name='program',
        ),
        migrations.AddField(
            model_name='allowedprogram',
            name='program_id',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='main.ProgramInfo'),
        ),
        migrations.AddField(
            model_name='allowedprogram',
            name='user_id',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='admitteduser',
            name='program_id',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='main.ProgramInfo'),
        ),
        migrations.AddField(
            model_name='admitteduser',
            name='user_id',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
    ]
