
from celery import shared_task
from .services import WalletOperations
import time
import random

@shared_task(bind=True, max_retries=3, default_retry_delay=3)
def send_notification(self, recipient_id, message):
    try:
        print(f"Отправка уведомления получателю {recipient_id}...")
        # Имитация долгого запроса
        time.sleep(5)
        
        # Симуляция случайной ошибки
        if random.random() < 0.5:
            raise Exception("Simulated sending failure")
        
        print(f"Уведомление получателю {recipient_id} отправлено: {message}")
        return True
    except Exception as exc:
        print(f"Ошибка отправки: {exc}. Попытка повторного запуска...")
        raise self.retry(exc=exc)

@shared_task(bind=True, max_retries=3, default_retry_delay=3)
def send_money(self, data, user_id, uuid_wallet):
    try:
        
        print("В очереди запрос...")
        operations = WalletOperations()

        # Имитация долгого запроса
        time.sleep(5)
        
        # Симуляция случайной ошибки
        if random.random() < 0.5:
            raise Exception("Simulated sending failure")

        operations.send_money(data, user_id, uuid_wallet)
        
        print("Запрос выполнен")
        send_notification.delay(
            recipient_id=data.get("recepient_uuid"),
            message="Вам пришли деньги!"
        )
        return True
    except Exception as exc:
        print(f"Ошибка отправки: {exc}. Попытка повторного запуска...")
        raise self.retry(exc=exc)