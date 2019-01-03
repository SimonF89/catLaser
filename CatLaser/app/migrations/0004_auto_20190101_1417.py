# Generated by Django 2.1.4 on 2019-01-01 13:17

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0003_auto_20181231_1839'),
    ]

    operations = [
        migrations.AlterField(
            model_name='edge',
            name='Nr',
            field=models.ForeignKey(limit_choices_to={'type': ('direction', 'Directional Vector')}, on_delete=django.db.models.deletion.CASCADE, related_name='Nr', to='app.Point', verbose_name='Normal Vector'),
        ),
        migrations.AlterField(
            model_name='edge',
            name='Vr',
            field=models.ForeignKey(limit_choices_to={'type': ('direction', 'Directional Vector')}, on_delete=django.db.models.deletion.CASCADE, related_name='Vr', to='app.Point', verbose_name='Direction Vector'),
        ),
        migrations.AlterField(
            model_name='point',
            name='type',
            field=models.CharField(choices=[('corner', 'Playground Corner'), ('run_point', 'Point inside the Playground'), ('direction', 'Directional Vector'), ('normal', 'Normal Vector')], default=('corner', 'Playground Corner'), max_length=50, verbose_name='Point Type'),
        ),
    ]