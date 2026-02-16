from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0004_remove_userprofile_created_at_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='ContactMessage',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('source', models.CharField(choices=[('user', 'User'), ('vendor', 'Vendor')], default='user', max_length=20)),
                ('name', models.CharField(max_length=120)),
                ('email', models.EmailField(max_length=254)),
                ('subject', models.CharField(max_length=200)),
                ('message', models.TextField()),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='auth.user')),
            ],
            options={
                'ordering': ['-created_at'],
            },
        ),
    ]
