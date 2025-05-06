import django
from django.conf import settings

# Minimal settings to satisfy Django
settings.configure(
    PASSWORD_HASHERS=['django.contrib.auth.hashers.PBKDF2PasswordHasher'],
)

django.setup()

from django.contrib.auth.hashers import make_password

hashed_password = make_password('123456')
print(hashed_password)
