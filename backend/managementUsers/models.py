from django.db import models
from backend.managementGroup.models import Group
from backend.subscription.models import Organization
from backend.LdapServer.models import ADServer
from django.contrib.auth.models import (AbstractBaseUser, BaseUserManager)
from django.utils.translation import gettext_lazy as _


class Permission(models.Model):
    name = models.CharField(max_length=200, null=True)
    context = models.CharField(max_length=200, null=True)

    class Meta:
        db_table = 'permission'

    def __str__(self):
        return self.name
    
class Roles(models.Model):
    name = models.CharField(max_length=200, null=True, unique=True, verbose_name=_("name"))
    fonctionalities = models.CharField(max_length=200, null=True)

    class Meta:
        db_table = 'roles'

    def __str__(self):
        return self.name


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
    username = models.CharField(max_length=200, null=True, unique=True, verbose_name=_("username"))
    password = models.CharField(max_length=800, null=True)
    email = models.CharField(max_length=800, null=True, unique=True)
    fullname = models.CharField(max_length=800, null=True)
    organisation = models.ForeignKey(
        Organization, on_delete=models.CASCADE, null=True)
    # role = models.CharField(max_length=800, null=True)
    # in case do u want to delete the usr after delete his role
    # role = models.ForeignKey(Roles, on_delete=models.CASCADE, null=True)
    #else
    role = models.ForeignKey(Roles, on_delete=models.SET_NULL, null=True)
    uid = models.IntegerField(null=True, unique=True)
    group = models.ManyToManyField(Group)
    permission = models.ManyToManyField(Permission)
    is_active = models.BooleanField(default=True)
    is_verified = models.BooleanField(default=False)
    token_last_expired = models.DateTimeField(null=True)
    objects = MyUserManager()
    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email']
    id_server = models.ForeignKey(ADServer, on_delete=models.SET_NULL, null=True)
    dn_user=models.CharField(max_length=900, null=True)

    class Meta:
        db_table = 'user'


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    phone_number = models.CharField(max_length=20, blank=False, null=True)
    region = models.CharField(max_length=100, blank=False, null=True)
    code_postal = models.CharField(max_length=20, blank=True, null=True)
    address = models.TextField(blank=False, null=True)
    country = models.CharField(max_length=100, blank=False, null=True)
    photo_url = models.CharField(blank=True, null=True, default='/media/profile/profile.jpg',max_length=1000)
    is_enable_2FA = models.BooleanField(default=False)
    language = models.CharField(max_length=100, default='en', null=True, blank=True)

    class Meta:
        db_table = 'profile'
