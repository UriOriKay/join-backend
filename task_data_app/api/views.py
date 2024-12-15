from rest_framework import generics
from task_data_app.models import Task, User, Category, SubTask
from .serializers import TaskSerializer, UserSerializer, RegisterSerializer, CategorySerializer, NewTaskSerializer, NewUserSerializer
from rest_framework.authtoken.views import APIView, ObtainAuthToken
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.authtoken.models import Token
from .permissions import IsStafforReadOnly, IsOwnerOAdmin
from datetime import datetime




class RegistrationView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        if request.data.get('contact'):
            request.data['password'] = "join356"
            request.data['repeated_password'] = "join356"
            request.data['is_active'] = False
        else:
            request.data['is_active'] = True

        serializer = RegisterSerializer(data=request.data)

        if serializer.is_valid():
            saved_account = serializer.save()
            token, created = Token.objects.get_or_create(user=saved_account)
            return Response({'message': 'Account created successfully',}, status=201)
        else:
            return Response(serializer.errors, status=200)


class CustomLoginView(ObtainAuthToken):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        
        data = {}
        if serializer.is_valid():
            user = serializer.validated_data['user']
            token, created = Token.objects.get_or_create(user=user)
            data = {
                'token': token.key,
                'name': user.name,
                'name_tag': user.name_tag
            }
        else:
            data = serializer.errors
        return Response(data)


class TaskViewSet(generics.ListCreateAPIView):
    queryset = Task.objects.all()
    serializer_class = TaskSerializer
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        data = serializer.data
        # print(data)
        transformed_data = []

        for task in data:
            transformed_task = {
                "container": task["container"],
                "category": task["category"],
                "title": task["title"],
                "description": task["description"],
                "date": task["due_date"],
                "priority": task["priority"],
                "priorityImg": task["priorityImg"],
                "associates": task["user"],
                "assignedTo": self.get_assigned_to_names(task["user"]),
                "assignedToNameTag": self.get_name_tags(task["user"]),
                "assignedToColor": self.get_assigned_colors(task["user"]),
                "subtasks": self.get_subtask_titles(task["subtask"]),
                "subtaskschecked": self.get_subtask_statuses(task["subtask"]),
                "id": task["id"],
            }
            transformed_data.append(transformed_task)

        return Response(transformed_data)

    def get_category_names(self, category_ids):
        # Convert category IDs to category names.
        return list(Category.objects.filter(id__in=category_ids).values_list('name', flat=True))

    def get_assigned_to_names(self, user_ids):
            # Convert user IDs to user names.
            return list(User.objects.filter(id__in=user_ids).values_list('name', flat=True))

    def get_name_tags(self, user_ids):
        # Generate name tags from user first and last names.
        return list(User.objects.filter(id__in=user_ids).values_list('name_tag', flat=True))

    def get_assigned_colors(self, user_ids):
        """Get assigned colors for users based on user IDs."""
        users = User.objects.filter(id__in=user_ids)
        return [user.color for user in users]

    def get_subtask_titles(self, subtask_ids):
        """Convert subtask IDs to subtask titles."""
        return list(SubTask.objects.filter(id__in=subtask_ids).values_list('name', flat=True))

    def get_subtask_statuses(self, subtask_ids):
        """Get the status (checked/unchecked) of subtasks."""
        subtasks = SubTask.objects.filter(id__in=subtask_ids)
        return ["checked" if subtask.checked else "unchecked" for subtask in subtasks]

    def post(self, request):
        serializer = NewTaskSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            all_tasks = TaskSerializer(Task.objects.all(), many=True).data
            return Response(all_tasks, status=201)
        else:
            return Response(serializer.errors, status=400)

    def put(self, request):
        task = Task.objects.get(id=request.data["id"])
        serilizer = TaskSerializer(task, data=request.data)
        if serilizer.is_valid():
            serilizer.save()
            all_tasks = TaskSerializer(Task.objects.all(), many=True).data
            return Response(all_tasks, status=201)
        else:
            return Response(serilizer.errors, status=400)

    def delete(self, request):
        task = Task.objects.get(id=request.data["id"])
        task.delete()
        all_tasks = TaskSerializer(Task.objects.all(), many=True).data
        return Response(all_tasks, status=201)


class TaskSummaryView(generics.ListAPIView):
    queryset = Task.objects.all()
    serializer_class = TaskSerializer

    def get(self, request):
        serializer = self.get_serializer(self.get_queryset(), many=True)
        summaryTasks = {
            0: 0,
            1: 0,
            2: 0,
            3: 0,
            4: 0,
            5: 0,
            6: None
        }
        for task in serializer.data:
            summaryTasks[1] += 1
            if task["priority"] == "Urgent":                
                summaryTasks[0] += 1 
            if task["container"] == "to-do-con":
                summaryTasks[2] += 1
            if task["container"] == "await-feedback-con":                
                summaryTasks[3] += 1
            if task["container"] == "in-progress-con":                
                summaryTasks[4] += 1                
            if task["container"] == "done-con":                
                summaryTasks[5] += 1

            task_due_date = datetime.strptime(task["due_date"], "%Y-%m-%d")
            if summaryTasks[6] is None or task_due_date < summaryTasks[6]:
                summaryTasks[6] = task_due_date

        summaryTasks[6] = summaryTasks[6].strftime("%Y-%m-%d")

        return Response(summaryTasks)


class AuthenticationView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        return Response({"message": "Authenticated"})




class UserViewSet(generics.ListCreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]
    def get(self, request):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        data = serializer.data
        contacts = []

        for user in data:
            transformed_user = {
                "id": user["id"],
                "name": user["name"],
                "name_tag": user["name_tag"],
                "color": user["color"],
                "phone": user["phone"],
                "email": user["email"]
            }
            contacts.append(transformed_user)
        return Response(contacts)
    
    def put (self, request):
        user = User.objects.get(id=request.data["id"])
        pw = user.password;
        serilizer = UserSerializer(user, data=request.data)
        if serilizer.is_valid():
            serilizer.validated_data['password'] = pw
            serilizer.save()
            all_users = UserSerializer(User.objects.all(), many=True).data
            return Response(all_users, status=201)
        else:
            return Response(serilizer.errors, status=400)
        
    def delete(self, request):
        user = User.objects.get(id=request.data["id"])
        user.delete()
        all_users = UserSerializer(User.objects.all(), many=True).data
        return Response(all_users, status=201)
    
    def post(self, request):
        serializer = NewUserSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            all_users = UserSerializer(User.objects.all(), many=True).data
            return Response(all_users, status=201)
        else:
            return Response(serializer.errors, status=400)


class UserDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsOwnerOAdmin]



class ContactViewSet(APIView):

    permission_classes = [IsAuthenticated]
    def get(self, request):
        pass

    def post(self, request):
        pass

    def put(self, request):
        pass

    def delete(self, request):
        pass

class CategoryViewSet(generics.ListCreateAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [IsAuthenticated]

    def get(self, request):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    