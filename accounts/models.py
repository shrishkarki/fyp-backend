import optparse
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager


class MyAccountManager(BaseUserManager):
    def create_user(self, email, username, password=None, **kwargs):
        if not email:
            raise ValueError('Users must have a valid email address.')
        if not username:
            raise ValueError('Users must have a valid username.')
        
        user = self.model(
            email=self.normalize_email(email),
            username=username,
        )
        
        user.set_password(password)
        user.save(using=self._db)
        return user
    
    def create_superuser(self, email, username, password):
        user = self.create_user(
            email=self.normalize_email(email),
            password=password,
            username=username,
        )
        user.is_admin = True
        user.is_superuser = True
        user.is_staff   = True
        user.save(using=self._db)


class Account(AbstractBaseUser):
    email        = models.EmailField(unique=True)
    username     = models.CharField(max_length=40,unique=True,null=True,blank=True)
    password     = models.CharField(max_length=128)
    date_joined  = models.DateTimeField(auto_now_add=True)
    last_login   = models.DateTimeField(auto_now=True)
    is_admin     = models.BooleanField(default=False)
    is_active    = models.BooleanField(default=True)
    is_staff     = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    
    name = models.CharField(max_length=40, blank=True)
    phone = models.CharField(max_length=10, blank=True)
    address = models.CharField(max_length=100, blank=True)
    otp = models.CharField(max_length=6,null=True,blank=True)
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username',]
    
    objects = MyAccountManager()
    
    def __str__(self):
        return self.email
    
    def has_perm(self, perm, obj=None):
        return self.is_admin
    
    def has_module_perms(self, app_label):
        return True
     

