from django.db import migrations, transaction

def create_users(apps, schema_editor):
    User = apps.get_model('users', 'User')  # если кастомная модель, заменяешь 'auth', 'User'
    
    users_data = [
        {'username': 'user1', 'password': 'password1'},
        {'username': 'user2', 'password': 'password2'},
        {'username': 'user3', 'password': 'password3'},
    ]

    with transaction.atomic():
        for data in users_data:
            user = User.objects.create_user(**data)

def delete_users(apps, schema_editor):
    User = apps.get_model('auth', 'User')
    User.objects.filter(username__in=['user1', 'user2', 'user3']).delete()

class Migration(migrations.Migration):

    dependencies = [
        ('users', '0001_initial'),  # замени на актуальную миграцию
    ]

    operations = [
        migrations.RunPython(create_users, reverse_code=delete_users),
    ]