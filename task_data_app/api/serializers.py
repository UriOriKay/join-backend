from rest_framework import serializers
from task_data_app.models import Task, User, Category, SubTask
import random

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'

class TaskSerializer(serializers.ModelSerializer):
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
        fields = ('email', 'name', 'password', 'repeated_password', 'is_active')
        extra_kwargs = {'password': {'write_only': True}}

    def save(self, **kwargs):
        print(self.validated_data)
        pw = self.validated_data['password']
        repeated_pw = self.validated_data['repeated_password']
        if pw != repeated_pw:
            raise serializers.ValidationError({'error': 'Passwords do not match'})
        account = User(
                    name=self.validated_data['name'], 
                    email=self.validated_data['email'],
                    name_tag=self.setNameTag(self.validated_data['name']),
                    color=self.SetRandomColor(),
                    phone=0,
                    is_active=self.validated_data['is_active']
                    )
        account.set_password(pw)
        account.save()

        return account
    
    def setNameTag(self, name):
        nameArray = name.split(' ')
        return nameArray[0][0] + nameArray[1][0]
    
    def SetRandomColor(self):
        randomNumber = random.randint(0, 17)
        if randomNumber == 1:
            return "--default" 
        else: 
            return f"--variant{str(randomNumber).zfill(2)}"
        


class NewTaskSerializer(serializers.ModelSerializer):
    subtask = serializers.ListField(
        child=serializers.JSONField(), required=False
    )
    category = serializers.PrimaryKeyRelatedField(many=True, queryset=Category.objects.all())
    class Meta:
        model = Task
        fields = '__all__'
    
    def save(self, **kwargs):
        category_data = self.validated_data.pop('category', [])
        user_data = self.validated_data.pop('user', [])
        subtask_data = self.validated_data.pop('subtask', [])

        task = Task.objects.create(
            container=self.validated_data['container'],
            title=self.validated_data['title'],
            description=self.validated_data['description'],
            due_date=self.validated_data['due_date'],
            priority=self.validated_data['priority'],
            priorityImg=self.validated_data['priorityImg'],
        )
        task.category.set(category_data)  # Set categories
        task.user.set(user_data)          # Set users


        for subtask in subtask_data:
            if isinstance(subtask, dict):  # New subtask
                new_subtask = SubTask.objects.create(**subtask)
                task.subtask.add(new_subtask)
            elif isinstance(subtask, int):  # Existing subtask
                existing_subtask = SubTask.objects.get(id=subtask)
                task.subtask.add(existing_subtask)


        task.save()
        return task


class NewUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = '__all__'