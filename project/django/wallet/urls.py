from django.urls import path
from .views import WalletRApiView, WalletCretaApiView, WalletUApiView

urlpatterns = [
    path('<uuid:uuid_wallet>', WalletRApiView.as_view(), name='balance-url'),
    path('create-wallet/', WalletCretaApiView.as_view(), name='create-wallet'),
    path('<uuid:uuid_wallet>/operation', WalletUApiView.as_view(), name='operations-wallet')
]