from django.db import models
from django.utils import timezone
from django.conf import settings
from django.contrib.auth.models import AbstractBaseUser
from django.contrib.auth.models import PermissionsMixin
from django.utils.translation import gettext_lazy as _
from .managers import CustomUserManager

class User(AbstractBaseUser, PermissionsMixin):
    name = models.CharField(_('names'), default='', max_length=50)
    last_name = models.CharField(_('last name'), default='', max_length=50)
    email = models.EmailField(_('email address'), unique=True)
    active_group = models.CharField(max_length=10, default='0', editable=False)
    verification_token = models.CharField('verification_token', max_length=30)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    date_joined = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = CustomUserManager()

    def __str__(self):
        return self.email

class Group(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField('nombre', max_length=50)
    status = models.CharField('estado', default='enable', choices=[(True, 'enable'), (False, 'disable')], editable=False, max_length=10)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

class Access(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    group = models.ForeignKey(Group, on_delete=models.CASCADE)
    date_joined = models.DateTimeField('fecha de ingreso', default=timezone.now)

    def __str__(self):
        return "%s, %s, %s" % (self.group.name, self.user.email, self.date_joined)

class Note(models.Model):
    id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=50)
    body = models.CharField(max_length=1000)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    group = models.ForeignKey(Group, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return "%s, %s, %s" % (self.group.name, self.user.email, self.updated_at)
