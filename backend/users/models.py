from django.db import models
from django.contrib.auth.models import (
    AbstractBaseUser, PermissionsMixin, UserManager
)
from django.core.validators import EmailValidator, RegexValidator
from django.core.files.base import ContentFile
import base64


class User(AbstractBaseUser, PermissionsMixin):
    """Модель для пользователей."""

    email = models.EmailField(
        unique=True,
        validators=[EmailValidator(
            message="Введите корректный адрес электронной почты.")]
    )

    username = models.CharField(
        max_length=150,
        unique=True,
        validators=[RegexValidator(regex=r'^[\w.@+-]+$',
                                   message='Username должен быть формата'
                                           '^[w.@+-]+Z')]
    )
    password = models.CharField(max_length=120, )
    first_name = models.CharField(max_length=120)
    last_name = models.CharField(max_length=120)
    is_subscribed = models.BooleanField(default=False)
    avatar = models.ImageField(upload_to='avatars', blank=True, null=True)
    REQUIRED_FIELDS = ['email', 'password', 'first_name', 'last_name']
    USERNAME_FIELD = 'username'
    is_staff = models.BooleanField(default=False)
    objects = UserManager()

    def __str__(self):
        """Возвращает username."""
        return self.username

    def set_avatar(self, base64_image, user):
        """base64 to file."""
        if base64_image.startswith('data:image/'):
            header, imgstr = base64_image.split(';base64,')
            ext = header.split('/')[1]
            file_name = f'avatar_{user}.{ext}'
            image = ContentFile(base64.b64decode(imgstr), name=file_name)
            self.avatar.save(file_name, image, save=True)
