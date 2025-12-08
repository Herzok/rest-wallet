from .models import Wallet, WalletTransactions
from users.models import User
from rest_framework.exceptions import NotFound, ValidationError, APIException
from .serializers import WalletSerializer
from django.db import transaction
from .constants import ADMIN_WALLET_UUID

class OperationTransactions:
    def get_money(wallet, amount):
        tax = None
        
        if amount > 1000:
            tax = round(amount * 0.1)
            total_amount = amount + tax
        else:
            total_amount = amount

        if wallet.balance < total_amount:
            raise ValidationError('Your balance is too low for transaction')
        
        try:
            serializer = WalletSerializer(instance=wallet,
                                          data={'balance': wallet.balance - total_amount},
                                          partial=True)
            serializer.is_valid(raise_exception=True)
        except Exception as e:
            raise APIException(str(e))

        return (tax, serializer)
    
    def deliver_money(wallet,amount):
        try:
            serializer = WalletSerializer(instance=wallet,
                                          data={'balance': wallet.balance + amount},
                                          partial=True)
            serializer.is_valid(raise_exception=True)
        except Exception as e:
            raise APIException(str(e))
        
        return serializer

    def get_tax_money(tax, wallet):
        try:
            serializer = WalletSerializer(instance=wallet,
                                          data={'balance': wallet.balance + tax},
                                          partial=True)
            serializer.is_valid(raise_exception=True)
        except Exception as e:
            raise APIException(str(e))
        
        return serializer

class Validator:
    def check_params_sm(self, data):
        try:
            if data.get('amount'):
                data['amount'] = int(data['amount'])
                if not data['amount'] != 0:
                    raise ValidationError("You've sent empty amount")
            else:
                raise ValidationError("You've sent empty amount")
        
        except ValueError:
            raise ValidationError("There are non-numeric characters")
        
        if not data.get('recepient_uuid'):
            raise ValidationError("You've sent empty recepient wallet")
        
        return data
    
class WalletOperations:
    validator = Validator()
    o_transacrions = OperationTransactions

    def send_money(self, data: dict, user: User | int, uuid_wallet: str):
        v_data = self.validator.check_params_sm(data)

        with transaction.atomic():
            your_wallet = self.get_wallet(uuid_wallet=uuid_wallet, user=user, for_update=True)
            recepient_wallet = self.get_wallet(uuid_wallet=v_data.get('recepient_uuid'), for_update=True)

            tax, serializer_your_wallet = self.o_transacrions.get_money(your_wallet, v_data.get('amount'))
            if tax:
                admin_wallet = self.get_wallet(uuid_wallet=ADMIN_WALLET_UUID, for_update=True)
                serializer_admin_wallet = self.o_transacrions.get_tax_money(tax, admin_wallet)

            serializer_recepient_wallet = self.o_transacrions.deliver_money(recepient_wallet,v_data.get('amount'))

            if tax:
                serializer_admin_wallet.save()
            serializer_your_wallet.save()
            serializer_recepient_wallet.save()

            WalletTransactions.objects.create(wallet=your_wallet, 
                                              text=f"{uuid_wallet} sent {v_data.get('amount')} to {v_data.get('recepient_uuid')}")
            
        return serializer_your_wallet.data

        

    def get_wallet(self, uuid_wallet=None, user=None, for_update=False):
        qs = Wallet.objects

        if for_update:
            qs = qs.select_for_update()

        try:
            if uuid_wallet and user:
                wallet = qs.get(user=user, wallet=uuid_wallet)
            elif uuid_wallet:
                wallet = qs.get(wallet=uuid_wallet)
        except Wallet.DoesNotExist:
            raise NotFound("Wallet not found")
        
        return wallet
        