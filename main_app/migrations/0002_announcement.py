# Generated by Django 5.1.4 on 2024-12-27 12:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main_app', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Announcement',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=255)),
                ('content', models.TextField()),
                ('priority', models.IntegerField(choices=[(1, 'High'), (2, 'Medium'), (3, 'Low')], default=3)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
        ),
    ]