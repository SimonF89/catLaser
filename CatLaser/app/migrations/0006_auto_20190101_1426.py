# Generated by Django 2.1.4 on 2019-01-01 13:26

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0005_auto_20190101_1418'),
    ]

    operations = [
        migrations.AlterField(
            model_name='edge',
            name='A',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='A', to='app.Point', verbose_name='Point A'),
        ),
        migrations.AlterField(
            model_name='edge',
            name='B',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='B', to='app.Point', verbose_name='Point B'),
        ),
        migrations.AlterField(
            model_name='edge',
            name='Nr',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='Nr', to='app.Point', verbose_name='Normal Vector'),
        ),
        migrations.AlterField(
            model_name='edge',
            name='Vr',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='Vr', to='app.Point', verbose_name='Direction Vector'),
        ),
    ]