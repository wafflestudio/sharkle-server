from django.contrib.auth.base_user import BaseUserManager, AbstractBaseUser
from django.db import models
import datetime
from django.utils.timezone import now
from random import randint

# Create your models here.
class CustomUserManager(BaseUserManager):
    use_in_migrations = True

    def _create_user(self, password, **extra_fields):
        user = self.model(**extra_fields)
        user.set_password(password)
        user.save(using=self._db)

        return user

    def create_user(self, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", False)
        extra_fields.setdefault("is_superuser", False)
        return self._create_user(password, **extra_fields)

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

    objects = CustomUserManager()

    EMAIL_FIELD = "email"
    USERNAME_FIELD = "email"

    user_id = models.CharField(max_length=20, unique=True)
    username = models.CharField(max_length=15)
    email = models.EmailField(max_length=30, unique=True)

    is_superuser = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)


class VerificationCode(models.Model):
    last_update = models.DateTimeField(auto_now=True)
    email = models.EmailField(max_length=100, unique=True, primary_key=True)
    code = models.PositiveIntegerField()

    def save(self, *args, **kwargs):
        self.code = randint(1000, 10000)
        super().save(*args, **kwargs)

    @classmethod
    def check_email_code(cls, email, submitted_code):
        time_limit = now() - datetime.timedelta(minutes=10)
        result = cls.objects.filter(
            email=email, code=submitted_code, last_update__gte=time_limit
        )
        if result.exists():
            return True
        return False
