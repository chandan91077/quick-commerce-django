from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('vendor', '0002_category_slug_product_slug_vendor_slug'),
    ]

    operations = [
        migrations.AlterField(
            model_name='vendor',
            name='pincode',
            field=models.CharField(
                max_length=200,
                help_text='Enter one or more 6-digit pincodes (comma separated)',
            ),
        ),
    ]
