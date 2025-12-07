from django.db import migrations, transaction
from wallet.constants import ADMIN_WALLET_UUID

def create_wallets(apps, schema_editor):
    User = apps.get_model('users', 'User')
    Wallet = apps.get_model('wallet', 'Wallet')

    with transaction.atomic():
        Wallet.objects.create(user=User.objects.get(username='user1'), balance=5000)
        Wallet.objects.create(user=User.objects.get(username='user2'), balance=1000, wallet=ADMIN_WALLET_UUID)
        Wallet.objects.create(user=User.objects.get(username='user3'), balance=1000)

def delete_wallets(apps, schema_editor):
    Wallet = apps.get_model('wallet', 'Wallet')
    usernames = ['user1', 'user2', 'user3']
    with transaction.atomic():
        Wallet.objects.filter(user__username__in=usernames).delete()

class Migration(migrations.Migration):

    dependencies = [
        ('wallet', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(create_wallets, reverse_code=delete_wallets),
    ]