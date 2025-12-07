import uuid
from users.models import User
from django.db import models
from django.core.validators import MaxValueValidator, MinValueValidator


class Wallet(models.Model):
    wallet = models.UUIDField(editable=False, default=uuid.uuid4, verbose_name='Кошелек')
    user = models.OneToOneField(to=User, related_name='OTO_key_User',
                                on_delete=models.CASCADE, verbose_name='Владелец')
    balance = models.IntegerField(verbose_name='Баланс',
                                  validators=[
                                      MinValueValidator(-1),
                                  ])

    class Meta:
        ordering = ['user']


class WalletTransactions(models.Model):
    transaction = models.UUIDField(editable=False, default=uuid.uuid4, verbose_name='Транзакция')
    wallet = models.ForeignKey(to=Wallet, related_name='F_Key_Wallet_WalletTransactions',
                                on_delete=models.CASCADE, verbose_name='Кошелек транзакции')
    date_create = models.DateField(verbose_name='Дата транзакции', auto_now_add=True)
    text = models.TextField(verbose_name='текст', max_length=255)

    class Meta:
        ordering = ['transaction']
