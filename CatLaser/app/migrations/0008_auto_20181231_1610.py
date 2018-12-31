# Generated by Django 2.1.4 on 2018-12-31 15:10

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0007_auto_20181231_1608'),
    ]

    operations = [
        migrations.AlterField(
            model_name='edge',
            name='playground',
            field=models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.CASCADE, to='app.Playground'),
        ),
        migrations.AlterField(
            model_name='point',
            name='playground',
            field=models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.CASCADE, to='app.Playground'),
        ),
    ]