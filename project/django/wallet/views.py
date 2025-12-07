from rest_framework import generics
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .models import Wallet
from .serializers import WalletSerializer
from django.conf import settings
from rest_framework import status
from .tasks import send_money
from .services import WalletOperations

class WalletUApiView(generics.RetrieveUpdateAPIView):
    permission_classes = [IsAuthenticated]
    operations = WalletOperations()

    def post(self, request, uuid_wallet):
        data = request.data.copy()
        if getattr(settings, "TESTING", False):
            return Response(self.operations.send_money(
                data=data, user=request.user, uuid_wallet=uuid_wallet))
        else:
            send_money.delay(data=data, user_id=request.user.id, uuid_wallet=uuid_wallet)
    
            return Response(
            {"status": "queued", "message": "Transaction is being processed"},
            status=status.HTTP_202_ACCEPTED
        )


class WalletRApiView(generics.RetrieveAPIView):
    permission_classes = [IsAuthenticated]
    operations = WalletOperations()

    def get(self, request, **kwargs):
        instance = self.operations.get_wallet(uuid_wallet=kwargs.get('uuid_wallet'),user=request.user)

        return Response(WalletSerializer(instance).data)


class WalletCretaApiView(generics.CreateAPIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        if Wallet.objects.filter(user=request.user).exists():
            raise ValidationError("Wallet for you exists")

        instance = Wallet.objects.create(user=self.request.user, balance=0)

        return Response(WalletSerializer(instance=instance).data)
