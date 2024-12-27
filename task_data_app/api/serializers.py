from rest_framework import serializers
from task_data_app.models import Task, User, Category, SubTask
import random
from .utils import authenticate_with_username_and_password


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'

class SubTaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = SubTask
        fields = ['name', 'checked']   

class TaskSerializer(serializers.ModelSerializer):
    subtask = serializers.PrimaryKeyRelatedField(many=True, read_only=True, source='subtask_set')
    class Meta:
        model = Task
        fields = '__all__'


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = '__all__'


class RegisterSerializer(serializers.ModelSerializer):
    repeated_password = serializers.CharField(write_only=True)
    class Meta:
        model = User
        fields = ('email', 'name', 'password', 'repeated_password', 'is_active', 'phone')
        extra_kwargs = {'password': {'write_only': True}}

    def save(self, **kwargs):
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
        nameArray = name.split(' ')
        return nameArray[0][0] + nameArray[1][0]
    
    def SetRandomColor(self):
        randomNumber = random.randint(1, 16)
        if randomNumber == 1:
            return "--default" 
        else: 
            return f"--variant{str(randomNumber).zfill(2)}"



class NewTaskSerializer(serializers.ModelSerializer):
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
        category_data = validated_data.pop('category', [])
        user_data = validated_data.pop('user', [])
        subtask_data = validated_data.pop('subtasks', [])

        task = Task.objects.create(**validated_data)
        task.category.set(category_data)  # Set categories
        task.user.set(user_data)          # Set users

        for subtask in subtask_data:
             SubTask.objects.create(task=task, **subtask)

        return task



    # def save(self, **kwargs):
    #     category_data = self.validated_data.pop('category', [])
    #     user_data = self.validated_data.pop('user', [])
    #     subtask_data = self.validated_data.pop('subtask', [])

    #     task = Task.objects.create(
    #         container=self.validated_data['container'],
    #         title=self.validated_data['title'],
    #         description=self.validated_data['description'],
    #         due_date=self.validated_data['due_date'],
    #         priority=self.validated_data['priority'],
    #         priorityImg=self.validated_data['priorityImg'],
    #     )
    #     task.category.set(category_data)  # Set categories
    #     task.user.set(user_data)          # Set users

    #     for subtask in subtask_data:
    #          SubTask.objects.create(task=task, **subtask)


    #     task.save()
    #     return task


class NewUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = '__all__'

class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(required=True, write_only=True)

    class Meta:
        model = User
        fields = ('email' 'password')
        read_only_fields = ('email',)
    
    def validate(self, attrs):
        user = authenticate_with_username_and_password(attrs['email'], attrs['password'])
        if user: 
            if user.is_active:
                return user
        raise serializers.ValidationError('Unable to log in with provided credentials.')
     