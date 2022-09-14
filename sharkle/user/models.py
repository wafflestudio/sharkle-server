from django.contrib.auth.base_user import BaseUserManager, AbstractBaseUser
from django.db import models
import datetime
from django.utils.timezone import now
from random import randint
from sharkle.upload_image import upload_image

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
        extra_fields.setdefault(
            "username", f"admin_{extra_fields.get('email').split('@')[0]}"
        )

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

    profile = models.ImageField(upload_to=upload_image, editable=True, null=True)

    username = models.CharField(max_length=20, unique=True)
    email = models.EmailField(max_length=30, unique=True)

    is_superuser = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)

    def has_perm(self, perm, obj=None):
        return self.is_superuser

    def has_module_perms(self, app_label):
        return self.is_superuser


class VerificationCode(models.Model):
    last_update = models.DateTimeField(auto_now=True)
    email = models.EmailField(max_length=100, unique=True, primary_key=True)
    code = models.PositiveIntegerField()

    def save(self, *args, **kwargs):
        self.code = randint(1000, 10000)
        super().save(*args, **kwargs)

    @classmethod
    def check_email_code(cls, email, submitted_code):
        # time_limit = now() - datetime.timedelta(minutes=10)
        result = cls.objects.filter(email=email, code=submitted_code)
        if result.exists():
            return True
        return False
