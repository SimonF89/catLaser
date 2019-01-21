# Generated by Django 2.1.4 on 2019-01-21 22:49

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0013_playground_active'),
    ]

    operations = [
        migrations.CreateModel(
            name='Point3D',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('x', models.FloatField(verbose_name='X-Value')),
                ('y', models.FloatField(verbose_name='Y-Value')),
                ('z', models.FloatField(verbose_name='Z-Value')),
                ('playground', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='app.Playground', verbose_name='Playground')),
            ],
        ),
    ]
