import uuid

from users.models import User
from .models import Wallet
from rest_framework.test import APIClient, APITestCase
from rest_framework import status
from django.urls import reverse
from .constants import ADMIN_WALLET_UUID
from django.test import override_settings


class WalletTestCase(APITestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(username='testuser1', password='zxc123')
        self.user2 = User.objects.create_user(username='testuser2', password='zxc123')
        self.user3 = User.objects.create_user(username='testuser3', password='zxc123')
        

        self.wallet1 = Wallet.objects.create(user=self.user1, balance=5000)
        self.wallet2 = Wallet.objects.create(user=self.user2, balance=1000, wallet=ADMIN_WALLET_UUID)
        self.wallet3 = Wallet.objects.create(user=self.user3, balance=2000)

        self.client = APIClient()
        response = self.client.post('/auth/token/login', {'username': 'testuser1', 'password': 'zxc123'}, format='json')
        self.token = response.data['auth_token']
        self.client.force_authenticate(user=self.user1, token=self.token)

        self.headers = {
            'Authorization': f'Token {self.token}',
            'Content-Type': 'application/json'
        }

    def test_get_wallet(self):
        urls = [
            reverse("balance-url", kwargs={"uuid_wallet": self.wallet1.wallet}),
            reverse("balance-url", kwargs={"uuid_wallet": uuid.uuid4()}),
        ]

        response = self.client.get(reverse("balance-url", kwargs={"uuid_wallet": self.wallet1.wallet}), **self.headers)
        # test right wallet
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['wallet'], str(self.wallet1.wallet))
        self.assertEqual(response.data['balance'], self.wallet1.balance)

        response = self.client.get(urls[1], **self.headers)
        # test wrong wallet
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data['detail'], 'Wallet not found')

    @override_settings(TESTING=True)
    def test_send_money(self): 
        urls = [ 
            reverse("operations-wallet", kwargs={"uuid_wallet": self.wallet1.wallet}), 
            reverse("operations-wallet", kwargs={"uuid_wallet": uuid.uuid4()}), 
        ] 
        

        response = self.client.post(urls[0], data={'recepient_uuid':self.wallet3.wallet, 'amount': '7000'}, **self.headers, format='json') 
        # test low balance for amount done
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST) 
        self.assertEqual(response.data[0], 'Your balance is too low for transaction') 

        response = self.client.post(urls[1], data={'recepient_uuid':self.wallet3.wallet, 'amount': '2'}, **self.headers, format='json') 
        # test wrong wallet done
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND) 
        self.assertEqual(response.data['detail'], 'Wallet not found') 
        
        response = self.client.post(urls[0], data={'recepient_uuid':self.wallet3.wallet, 'amount': '2sdgsgh'}, **self.headers, format='json') 
        # test wrong type amount done
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST) 
        self.assertEqual(response.data[0], "There are non-numeric characters")
        
        response = self.client.post(urls[0], data={'recepient_uuid':self.wallet3.wallet, 'amount': '0'}, **self.headers, format='json') 
        # test empty amount done
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST) 
        self.assertEqual(response.data[0], "You've sent empty amount") 

        response = self.client.post(urls[0], data={'recepient_uuid':'', 'amount': '200'}, **self.headers, format='json') 
        # test empty recepient wallet done
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST) 
        self.assertEqual(response.data[0], "You've sent empty recepient wallet") 

        response = self.client.post(urls[0], data={'recepient_uuid':self.wallet3.wallet, 'amount': '100'}, **self.headers, format='json') 
        wallet1_old_balance = self.wallet1.balance 
        wallet3_old_balance = self.wallet3.balance 
        self.wallet1 = Wallet.objects.get(user=self.user1) 
        self.wallet3 = Wallet.objects.get(user=self.user3) 
        # test send money 
        self.assertIsInstance(self.wallet3, Wallet) 
        self.assertIsInstance(self.wallet1, Wallet)
        self.assertEqual(response.status_code, status.HTTP_200_OK) 
        self.assertEqual(self.wallet3.balance, wallet3_old_balance + 100) 
        self.assertEqual(self.wallet1.balance, wallet1_old_balance - 100) 

        response = self.client.post(urls[0], data={'recepient_uuid':self.wallet3.wallet, 'amount': '1200'}, **self.headers, format='json') 
        wallet1_old_balance = self.wallet1.balance 
        wallet2_old_balance = self.wallet2.balance 
        wallet3_old_balance = self.wallet3.balance 
        self.wallet1 = Wallet.objects.get(user=self.user1) 
        self.wallet3 = Wallet.objects.get(user=self.user3) 
        self.wallet2 = Wallet.objects.get(user=self.user2) 
        # test send money with tax 
        self.assertEqual(response.status_code, status.HTTP_200_OK) 
        self.assertEqual(self.wallet3.balance, wallet3_old_balance + 1200) 
        self.assertEqual(self.wallet1.balance, wallet1_old_balance - (1200 + round(1200*0.1))) 
        self.assertEqual(self.wallet2.balance, wallet2_old_balance + round(1200*0.1)) 
        
        self.wallet3.delete() 
        response = self.client.post(urls[0], data={'recepient_uuid':self.wallet3.wallet, 'amount': '2'}, **self.headers, format='json') 
        # test wallet not found 
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND) 
        self.assertEqual(response.data['detail'], 'Wallet not found')


    def test_create_wallet(self):
        response = self.client.post(reverse('create-wallet'), **self.headers)
        # test create wallet
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data[0], "Wallet for you exists")

        self.wallet1.delete()
        response = self.client.post(reverse('create-wallet'), **self.headers)
        self.wallet1 = Wallet.objects.get(user=self.user1)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(str(self.wallet1.wallet), response.data['wallet'])
        self.assertEqual(self.wallet1.balance, response.data['balance'])
