# Generated by Django 2.1.4 on 2019-01-21 23:40

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0020_auto_20190122_0039'),
    ]

    operations = [
        migrations.AlterField(
            model_name='point3d',
            name='playground',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='app.Playground', verbose_name='Laser'),
        ),
    ]
