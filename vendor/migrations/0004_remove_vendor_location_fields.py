from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('vendor', '0003_vendor_multi_pincode'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='vendor',
            name='delivery_radius',
        ),
        migrations.RemoveField(
            model_name='vendor',
            name='latitude',
        ),
        migrations.RemoveField(
            model_name='vendor',
            name='longitude',
        ),
    ]
