from django.utils import timezone
from django.db import models
from backend.managementGroup.models import *
from backend.subscription.models import *
from backend.LdapServer.models import ADServer
from django.contrib.auth.models import (AbstractBaseUser, BaseUserManager)
# Create your models here.


class Permission(models.Model):
    name = models.CharField(max_length=200, null=True)
    context = models.CharField(max_length=200, null=True)

    class Meta:
        db_table = 'permission'

    def __str__(self):
        return self.name

##
# Create your models here


class MyUserManager(BaseUserManager):
    def create_user(self, username, password=None):
        """
        Creates and saves a User with the given username and password.
        """
        if not username:
            raise ValueError('Users must have an username')

        user = self.model(
            username=self.normalize_email(),

        )

        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, password=None):
        """
        Creates and saves a superuser with the given username and password.
        """
        user = self.create_user(
            username,
            password=password,

        )
        user.is_admin = True
        user.save(using=self._db)
        return user


class User(AbstractBaseUser):
    username = models.CharField(max_length=200, null=True, unique=True)
    password = models.CharField(max_length=800, null=True)
    email = models.CharField(max_length=800, null=True, unique=True)
    fullname = models.CharField(max_length=800, null=True)
    organisation = models.ForeignKey(
        organization, on_delete=models.CASCADE, null=True)
    role = models.CharField(max_length=800, null=True)
    uid = models.IntegerField(null=True, unique=True)
    group = models.ManyToManyField(Group)
    permission = models.ManyToManyField(Permission)
    is_active = models.BooleanField(default=True)
    is_verified = models.BooleanField(default=False)
    token_last_expired = models.DateTimeField(null=True)
    objects = MyUserManager()
    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email']
    id_server = models.ForeignKey(ADServer, on_delete=models.CASCADE, null=True)

    class Meta:
        db_table = 'user'

    # def __str__(self):
    #     return self.username
