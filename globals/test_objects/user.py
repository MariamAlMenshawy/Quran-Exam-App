from accounts.models import User

def create_user(
    email='test@gmail.com',
    password='test12345',
):
    return User.objects.create_user(
        email=email,
        password=password,
    )