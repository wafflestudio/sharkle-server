from django.contrib.auth.base_user import BaseUserManager, AbstractBaseUser
from django.db import models

# Create your models here.
class CustomUserManager(BaseUserManager):

    use_in_migrations = True

    def _create_user(self, user_id, password, **extra_fields):
        user = self.model(user_id=user_id, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)

        return user

    def create_user(self, user_id, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", False)
        extra_fields.setdefault("is_superuser", False)
        return self._create_user(user_id, password, **extra_fields)

    def create_superuser(self, password, **extra_fields):

        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        if (
            extra_fields.get("is_staff") is not True
            or extra_fields.get("is_superuser") is not True
        ):
            raise ValueError("권한 설정이 잘못되었습니다.")

        return self._create_user(password, **extra_fields)


class User(AbstractBaseUser):

    EMAIL_FIELD = "email"
    USERNAME_FIELD = "email"  # TODO ?

    username = models.CharField(max_length=50)
    email = models.EmailField(max_length=30, unique=True)  # TODO unique ?
