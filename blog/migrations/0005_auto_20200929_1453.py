# Generated by Django 3.0.6 on 2020-09-29 09:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0004_auto_20200929_1450'),
    ]

    operations = [
        migrations.AlterField(
            model_name='jobapplication',
            name='resume',
            field=models.FileField(default='default.jpg', upload_to='profile_pics'),
        ),
    ]
