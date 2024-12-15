from django.contrib.auth.models import UserManager, PermissionsMixin, AbstractBaseUser
from django.db import models
from django.utils import timezone
# Create your models here.


class CustomUserManager(UserManager):
    def _create_user(self, email, password, **extra_fields):
        if not email:
            raise ValueError("You have not provided a valid email address")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", False)
        extra_fields.setdefault("is_superuser", False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")

        return self._create_user(email, password, **extra_fields)
    
class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(blank=True, unique=True, default='')
    name = models.CharField(max_length=250, blank=True, default='')
    name_tag = models.CharField(max_length=2, blank=True, default='')
    color = models.CharField(max_length=15, blank=True, default='')
    phone = models.IntegerField(blank=True, default=0)

    is_active = models.BooleanField(default=True)
    is_superuser = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)

    date_joined = models.DateTimeField(default=timezone.now)
    last_login = models.DateTimeField(blank=True, null=True)
    
    objects = CustomUserManager()

    USERNAME_FIELD = 'email'
    EMAIL_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = CustomUserManager()

    class Meta:
        verbose_name = "User"
        verbose_name_plural = "Users"

    def get_full_name(self):
        return self.name

    def get_short_name(self):
        return self.name or self.email.split('@')[0]

    def __str__(self):
        return self.name
    
class Category(models.Model):
    name = models.CharField(max_length=30, blank=True, default='', unique=True)
    color = models.CharField(max_length=15, blank=True, default='')
    name_tag = models.CharField(max_length=2, blank=True, default='')

    def __str__(self):
        
        return self.name
    
class SubTask(models.Model):
    name = models.CharField(max_length=50, blank=True, default='')
    checked = models.BooleanField(default=False)

    def __str__(self):
        return self.name

class Task(models.Model):
    container = models.CharField(max_length=30, blank=True, default='')
    title = models.CharField(max_length=50, blank=True, default='')
    category = models.ManyToManyField(Category, related_name='task', blank=True)
    description = models.CharField(max_length=250, blank=True, default='')
    due_date = models.DateField(blank=True, null=True)
    priority = models.CharField(max_length=25, blank=True)
    priorityImg = models.CharField(max_length=50, blank=True)
    user = models.ManyToManyField(User, related_name='task', blank=True)
    subtask = models.ManyToManyField(SubTask, related_name='task', blank=True)
    
    def __str__(self):   
        return self.title
