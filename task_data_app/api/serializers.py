from rest_framework import serializers
from task_data_app.models import Task, User, Category, SubTask
import random
from .utils import authenticate_with_username_and_password


class CategorySerializer(serializers.ModelSerializer):
    """
    Serializer for the `Category` model.

    Meta
    ----
    model : Category
        The model associated with this serializer.
    fields : str
        All fields in the `Category` model are included.
    """
    class Meta:
        model = Category
        fields = '__all__'

class SubTaskSerializer(serializers.ModelSerializer):
    """
    Serializer for the `SubTask` model.

    Meta
    ----
    model : SubTask
        The model associated with this serializer.
    fields : list
        Includes `name` and `checked` fields.
    """
    class Meta:
        model = SubTask
        fields = ['name', 'checked']   

class TaskSerializer(serializers.ModelSerializer):
    """
    Serializer for the `Task` model.

    Attributes
    ----------
    subtask : PrimaryKeyRelatedField
        Field to include related subtasks in the serialized data.

    Meta
    ----
    model : Task
        The model associated with this serializer.
    fields : str
        All fields in the `Task` model are included.
    """
    subtask = serializers.PrimaryKeyRelatedField(many=True, read_only=True, source='subtask_set')
    class Meta:
        model = Task
        fields = '__all__'


class UserSerializer(serializers.ModelSerializer):
    """
    Serializer for the `User` model.

    Meta
    ----
    model : User
        The model associated with this serializer.
    fields : str
        All fields in the `User` model are included.
    """
    class Meta:
        model = User
        fields = '__all__'


class RegisterSerializer(serializers.ModelSerializer):
    """
    Serializer for user registration.

    Attributes
    ----------
    repeated_password : CharField
        Field to confirm the user's password.

    Methods
    -------
    save(**kwargs)
        Validates passwords and creates a new user instance.
    setNameTag(name)
        Generates a short name tag from the user's full name.
    SetRandomColor()
        Assigns a random color to the user.

    Meta
    ----
    model : User
        The model associated with this serializer.
    fields : tuple
        Includes `email`, `name`, `password`, `repeated_password`, `is_active`, and `phone`.
    extra_kwargs : dict
        Ensures passwords are write-only.
    """
    repeated_password = serializers.CharField(write_only=True)
    class Meta:
        model = User
        fields = ('email', 'name', 'password', 'repeated_password', 'is_active', 'phone')
        extra_kwargs = {'password': {'write_only': True}}

    def save(self, **kwargs):
        """
        Validates passwords and creates a new user instance.

        Parameters
        ----------
        **kwargs : dict
            Additional arguments for the save method.

        Returns
        -------
        User
            The created user instance.
        """
        pw = self.validated_data['password']
        repeated_pw = self.validated_data['repeated_password']
        if pw != repeated_pw:
            raise serializers.ValidationError({'error': 'Passwords do not match'})
        account = User(
                    name=self.validated_data['name'], 
                    email=self.validated_data['email'],
                    name_tag=self.setNameTag(self.validated_data['name']),
                    color=self.SetRandomColor(),
                    phone=self.validated_data['phone'],
                    is_active=self.validated_data['is_active']
                    )
        account.set_password(pw)
        account.save()

        return account
    
    def setNameTag(self, name):
        """
        Generates a short name tag from the user's full name.

        Parameters
        ----------
        name : str
            The user's full name.

        Returns
        -------
        str
            The generated name tag.
        """
        nameArray = name.split(' ')
        return nameArray[0][0] + nameArray[1][0]
    
    def SetRandomColor(self):
        """
        Assigns a random color to the user.

        Returns
        -------
        str
            A string representing the randomly assigned color.
        """
        randomNumber = random.randint(1, 16)
        if randomNumber == 1:
            return "--default" 
        else: 
            return f"--variant{str(randomNumber).zfill(2)}"



class NewTaskSerializer(serializers.ModelSerializer):
    """
    Serializer for creating a new task.

    Attributes
    ----------
    category : PrimaryKeyRelatedField
        Field for related categories.
    user : PrimaryKeyRelatedField
        Field for related users.
    subtasks : SubTaskSerializer
        Nested serializer for related subtasks.

    Methods
    -------
    create(validated_data)
        Creates a new task with associated categories, users, and subtasks.

    Meta
    ----
    model : Task
        The model associated with this serializer.
    fields : str
        All fields in the `Task` model are included.
    """
    category = serializers.PrimaryKeyRelatedField(
        many=True, queryset=Category.objects.all())
    user = serializers.PrimaryKeyRelatedField(
        many=True, queryset=User.objects.all())
    # Nested serializer for subtasks
    subtasks = SubTaskSerializer(many=True, required=False)
    
    class Meta:
        model = Task
        fields = '__all__'
    
    def create(self, validated_data):
        """
        Creates a new task with associated categories, users, and subtasks.

        Parameters
        ----------
        validated_data : dict
            The validated data for creating the task.

        Returns
        -------
        Task
            The created task instance.
        """
        category_data = validated_data.pop('category', [])
        user_data = validated_data.pop('user', [])
        subtask_data = validated_data.pop('subtasks', [])

        task = Task.objects.create(**validated_data)
        task.category.set(category_data)  # Set categories
        task.user.set(user_data)          # Set users

        for subtask in subtask_data:
             SubTask.objects.create(task=task, **subtask)

        return task


class NewUserSerializer(serializers.ModelSerializer):
    """
    Serializer for creating a new user.

    Meta
    ----
    model : User
        The model associated with this serializer.
    fields : str
        All fields in the `User` model are included.
    """
    class Meta:
        model = User
        fields = '__all__'

class LoginSerializer(serializers.Serializer):
    """
    Serializer for user login.

    Attributes
    ----------
    email : EmailField
        The email address of the user.
    password : CharField
        The user's password.

    Methods
    -------
    validate(attrs)
        Validates the user's credentials.

    Meta
    ----
    model : User
        The model associated with this serializer.
    fields : tuple
        Includes `email` and `password`.
    read_only_fields : tuple
        Specifies `email` as a read-only field.
    """
    email = serializers.EmailField()
    password = serializers.CharField(required=True, write_only=True)

    class Meta:
        model = User
        fields = ('email' 'password')
        read_only_fields = ('email',)
    
    def validate(self, attrs):
        """
        Validates the user's credentials.

        Parameters
        ----------
        attrs : dict
            The input data containing email and password.

        Returns
        -------
        User
            The authenticated user.

        Raises
        ------
        serializers.ValidationError
            If the credentials are invalid or the user is inactive.
        """
        user = authenticate_with_username_and_password(attrs['email'], attrs['password'])
        if user: 
            if user.is_active:
                return user
        raise serializers.ValidationError('Unable to log in with provided credentials.')
     