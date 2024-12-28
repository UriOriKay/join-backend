from django.contrib.auth.models import UserManager, PermissionsMixin, AbstractBaseUser
from django.db import models
from django.utils import timezone
# Create your models here.


class CustomUserManager(UserManager):
    """
    Custom manager for the User model with methods to create regular and superusers.

    Methods
    -------
    _create_user(email, password, **extra_fields)
        Creates and saves a User with the specified email and password.
    create_user(email, password=None, **extra_fields)
        Creates and saves a regular User.
    create_superuser(email, password=None, **extra_fields)
        Creates and saves a SuperUser.
    """



    def _create_user(self, email, password, **extra_fields):
        """
        Creates and saves a User with the specified email and password.

        Parameters
        ----------
        email : str
            The email address of the user.
        password : str
            The password for the user.
        **extra_fields : dict
            Additional fields for the user.

        Returns
        -------
        User
            The created User instance.
        """
        if not email:
            raise ValueError("You have not provided a valid email address")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password=None, **extra_fields):
        """
        Creates and saves a regular User.

        Parameters
        ----------
        email : str
            The email address of the user.
        password : str, optional
            The password for the user (default is None).
        **extra_fields : dict
            Additional fields for the user.

        Returns
        -------
        User
            The created User instance.
        """
        extra_fields.setdefault("is_staff", False)
        extra_fields.setdefault("is_superuser", False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password=None, **extra_fields):
        """
        Creates and saves a SuperUser.

        Parameters
        ----------
        email : str
            The email address of the superuser.
        password : str, optional
            The password for the superuser (default is None).
        **extra_fields : dict
            Additional fields for the superuser.

        Raises
        ------
        ValueError
            If `is_staff` or `is_superuser` is not set to True.

        Returns
        -------
        User
            The created SuperUser instance.
        """
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")

        return self._create_user(email, password, **extra_fields)
    
class User(AbstractBaseUser, PermissionsMixin):
    """
    Custom User model with email as the unique identifier instead of username.

    Attributes
    ----------
    email : str
        The email address of the user.
    name : str
        The full name of the user.
    name_tag : str
        A short name tag for the user.
    color : str
        The color assigned to the user.
    phone : int
        The phone number of the user.
    is_active : bool
        Indicates whether the user account is active.
    is_superuser : bool
        Indicates whether the user has superuser privileges.
    is_staff : bool
        Indicates whether the user is a staff member.
    date_joined : datetime
        The date when the user joined.
    last_login : datetime
        The date of the user's last login.

    Methods
    -------
    get_full_name()
        Returns the full name of the user.
    get_short_name()
        Returns the first part of the user's name or email username.
    save(*args, **kwargs)
        Saves the user instance, ensuring the password is hashed if provided.
    """
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
        """
        Returns the full name of the user.

        Returns
        -------
        str
            The user's full name.
        """
        return self.name

    def get_short_name(self):
        """
        Returns the first part of the user's name or email username.

        Returns
        -------
        str
            The user's short name.
        """
        return self.name or self.email.split('@')[0]
    
    def save(self, *args, **kwargs):
        """
        Saves the user instance, ensuring the password is hashed if provided.

        Parameters
        ----------
        *args : tuple
            Positional arguments for the save method.
        **kwargs : dict
            Keyword arguments for the save method.
        """
        if self.password:
            self.set_password(self.password)
        super().save(*args, **kwargs)
        

    def __str__(self):
        """
        Returns a string representation of the user.

        Returns
        -------
        str
            The user's name.
        """
        return self.name
    
class Category(models.Model):
    """
    Model for representing a task category.

    Attributes
    ----------
    name : str
        The name of the category.
    color : str
        The color assigned to the category.
    name_tag : str
        A short name tag for the category.
    """
    name = models.CharField(max_length=30, blank=True, default='', unique=True)
    color = models.CharField(max_length=15, blank=True, default='')
    name_tag = models.CharField(max_length=2, blank=True, default='')

    def __str__(self):
        """
        Returns a string representation of the category.

        Returns
        -------
        str
            The category's name.
        """
        return self.name
    

class Task(models.Model):
    """
    Model for representing a task.

    Attributes
    ----------
    container : str
        The container to which the task belongs.
    title : str
        The title of the task.
    category : ManyToManyField
        The categories associated with the task.
    description : str
        The description of the task.
    due_date : date
        The due date for the task.
    priority : str
        The priority level of the task.
    priorityImg : str
        The image URL associated with the task's priority.
    user : ManyToManyField
        The users associated with the task.
    """
    container = models.CharField(max_length=30, blank=True, default='')
    title = models.CharField(max_length=50, blank=True, default='')
    category = models.ManyToManyField(Category, related_name='task', blank=True)
    description = models.CharField(max_length=250, blank=True, default='')
    due_date = models.DateField(blank=True, null=True)
    priority = models.CharField(max_length=25, blank=True)
    priorityImg = models.CharField(max_length=50, blank=True)
    user = models.ManyToManyField(User, related_name='task', blank=True)
    
    def __str__(self):
        """
        Returns a string representation of the task.

        Returns
        -------
        str
            The task's title.
        """  
        return self.title
    
class SubTask(models.Model):
    """
    Model for representing a subtask related to a parent task.

    Attributes
    ----------
    task : ForeignKey
        The parent task to which the subtask belongs.
    name : str
        The name of the subtask.
    checked : bool
        Indicates whether the subtask is completed.
    """
    task = models.ForeignKey(Task, on_delete=models.CASCADE, null=True)
    name = models.CharField(max_length=50, blank=True, default='')
    checked = models.BooleanField(default=False)

    def __str__(self):
        """
        Returns a string representation of the subtask.

        Returns
        -------
        str
            The subtask's name.
        """
        return self.name
