from datetime import datetime

from rest_framework import generics
from rest_framework.authtoken.models import Token
from rest_framework.authtoken.views import APIView, ObtainAuthToken
from rest_framework.permissions import IsAuthenticated, AllowAny
from task_data_app.models import Task, User, Category, SubTask
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth import get_user_model

from .serializers import (
    TaskSerializer, 
    UserSerializer, 
    RegisterSerializer, 
    CategorySerializer, 
    NewTaskSerializer, 
    NewUserSerializer,
    LoginSerializer,
)
from .permissions import IsOwnerOAdmin




class RegistrationView(APIView):
    """
    API view for user registration.

    Methods
    -------
    post(request)
        Handles the registration of a new user.
    """
    permission_classes = [AllowAny]

    def post(self, request):
        """
        Handles the registration of a new user.

        Parameters
        ----------
        request : Request
            The HTTP request containing user registration data.

        Returns
        -------
        Response
            A response indicating the success or failure of the registration.
        """
        if request.data.get('contact'):
            request.data['password'] = "join356"
            request.data['repeated_password'] = "join356"
            request.data['is_active'] = False


        else:
            request.data['is_active'] = True
            request.data['phone'] = 0

        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            print(serializer.validated_data['password'] )
            saved_account = serializer.save()
            token, created = Token.objects.get_or_create(user=saved_account)
            return Response({'message': 'Account created successfully',}, status=201)
        return Response(serializer.errors, status=200)


class CustomLoginView(ObtainAuthToken):
    """
    Custom API view for user login.

    Methods
    -------
    post(request)
        Handles user authentication and token generation.
    """
    permission_classes = [AllowAny]
    serializer_class = LoginSerializer
    def post(self, request):
        """
        Handles user authentication and token generation.

        Parameters
        ----------
        request : Request
            The HTTP request containing login credentials.

        Returns
        -------
        Response
            A response with the user's token and additional information.
        """
        serializer = self.serializer_class(data=request.data)
        print("serializer", serializer)
        print("serializer.data", serializer.is_valid())
        data = {}
        try:
            serializer.is_valid(raise_exception=True)
        except Exception as e:
            print(e)
            return Response({'error': 'Wrong username or password'}, status=status.HTTP_401_UNAUTHORIZED)
        if serializer.is_valid():
            user_data = serializer.validated_data
            if user_data.email:
                try:
                    token, created = Token.objects.get_or_create(user=user_data)
                    data = {
                        'token': token.key,
                        'name': user_data.name,
                        'name_tag': user_data.name_tag
                    }
                    return Response(data, status=status.HTTP_200_OK)
                except User.DoesNotExist:
                    print("User does not exist")
                    return Response({'error': 'User does not exist'}, status=status.HTTP_404_NOT_FOUND)
        else:
            user_data = serializer.data
            print("user_data")
            if serializer.data.get('email'):
                try:
                    user=get_user_model().objects.get(email=user_data['email'])
                    if not user.is_active:
                        return Response({'error': 'User is not active'}, status=status.HTTP_403_FORBIDDEN)
                    else:
                        print("wrong password")
                        return Response({'error': 'Wrong username or password'}, status=status.HTTP_401_UNAUTHORIZED)
                except get_user_model().DoesNotExist:
                    return Response({'error': 'User does not exist'}, status=status.HTTP_404_NOT_FOUND)
            else:
                return Response({'error': 'Email field is requiered'}, status=status.HTTP_400_BAD_REQUEST)



class TaskViewSet(generics.ListCreateAPIView):
    """
    ViewSet for managing tasks.

    Methods
    -------
    get(request, *args, **kwargs)
        Retrieves all tasks.
    post(request)
        Creates a new task.
    put(request)
        Updates an existing task.
    delete(request)
        Deletes a task.
    """
    queryset = Task.objects.all()
    serializer_class = TaskSerializer
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        """
        Retrieves all tasks with detailed transformation.

        Parameters
        ----------
        request : Request
            The HTTP request.

        Returns
        -------
        Response
            A response containing transformed task data.
        """
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        data = serializer.data
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
        """
        Converts category IDs to category names.

        Parameters
        ----------
        category_ids : list of int
            List of IDs corresponding to the categories.

        Returns
        -------
        list of str
            List of category names associated with the provided IDs.
        """
        return list(Category.objects.filter(id__in=category_ids).values_list('name', flat=True))

    def get_assigned_to_names(self, user_ids):
        """
        Converts user IDs to user names.

        Parameters
        ----------
        user_ids : list of int
            List of user IDs associated with the task.

        Returns
        -------
        list of str
            List of names corresponding to the provided user IDs.
        """
        return list(User.objects.filter(id__in=user_ids).values_list('name', flat=True))

    def get_name_tags(self, user_ids):
        """
        Generates name tags from user IDs.

        Parameters
        ----------
        user_ids : list of int
            List of user IDs associated with the task.

        Returns
        -------
        list of str
            List of name tags corresponding to the provided user IDs.
        """
        return list(User.objects.filter(id__in=user_ids).values_list('name_tag', flat=True))

    def get_assigned_colors(self, user_ids):
        """
        Retrieves assigned colors for users based on their IDs.

        Parameters
        ----------
        user_ids : list of int
            List of user IDs associated with the task.

        Returns
        -------
        list of str
            List of colors corresponding to the provided user IDs.
        """
        users = User.objects.filter(id__in=user_ids)
        return [user.color for user in users]

    def get_subtask_titles(self, subtask_ids):
        """
        Converts subtask IDs to subtask titles.

        Parameters
        ----------
        subtask_ids : list of int
            List of subtask IDs associated with the task.

        Returns
        -------
        list of str
            List of subtask titles corresponding to the provided IDs.
        """
        return list(SubTask.objects.filter(id__in=subtask_ids).values_list('name', flat=True))

    def get_subtask_statuses(self, subtask_ids):
        """
        Retrieves the status (checked/unchecked) of subtasks.

        Parameters
        ----------
        subtask_ids : list of int
            List of subtask IDs associated with the task.

        Returns
        -------
        list of str
            List of subtask statuses where each status is either "checked" or "unchecked".
        """
        subtasks = SubTask.objects.filter(id__in=subtask_ids)
        return ["checked" if subtask.checked else "unchecked" for subtask in subtasks]

    def post(self, request):
        """
        Creates a new task.

        Parameters
        ----------
        request : Request
            The HTTP request containing task data.

        Returns
        -------
        Response
            A response with the created task data or errors.
        """
        serializer = NewTaskSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            all_tasks = TaskSerializer(Task.objects.all(), many=True).data
            return Response(all_tasks, status=201)
        else:
            return Response(serializer.errors, status=400)

    def put(self, request):
        """
        Updates an existing task.

        Parameters
        ----------
        request : Request
            The HTTP request containing updated task data.

        Returns
        -------
        Response
            A response with the updated task data or errors.
        """
        task = Task.objects.get(id=request.data["id"])
        serilizer = TaskSerializer(task, data=request.data)
        if serilizer.is_valid():
            serilizer.save()
            all_tasks = TaskSerializer(Task.objects.all(), many=True).data
            return Response(all_tasks, status=201)
        else:
            return Response(serilizer.errors, status=400)

    def delete(self, request):
        """
        Deletes a task.

        Parameters
        ----------
        request : Request
            The HTTP request containing the task ID to delete.

        Returns
        -------
        Response
            A response with the remaining tasks after deletion.
        """
        task = Task.objects.get(id=request.data["id"])
        task.delete()
        all_tasks = TaskSerializer(Task.objects.all(), many=True).data
        return Response(all_tasks, status=201)


class TaskSummaryView(generics.ListAPIView):
    """
    View for retrieving task summaries.

    Methods
    -------
    get(request)
        Retrieves a summary of tasks, including priority counts and due dates.
    """
    queryset = Task.objects.all()
    serializer_class = TaskSerializer

    def get(self, request):
        """
        Retrieves a summary of tasks, including counts by priority and containers.

        Parameters
        ----------
        request : Request
            The HTTP request.

        Returns
        -------
        Response
            A response with task summary data.
        """
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
    """
    ViewSet for managing user-related operations.

    Attributes
    ----------
    queryset : QuerySet
        The queryset containing all User instances.
    serializer_class : Serializer
        The serializer class for serializing and deserializing User instances.
    permission_classes : list
        Permissions required to access the view.

    Methods
    -------
    get(request)
        Retrieves all users in a transformed format.
    put(request)
        Updates an existing user's details.
    delete(request)
        Deletes a user by ID.
    post(request)
        Creates a new user.
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]
    def get(self, request):
        """
        Retrieves all users and transforms their data.

        Parameters
        ----------
        request : Request
            The HTTP request.

        Returns
        -------
        Response
            A response containing transformed user data.
        """
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
        """
        Updates an existing user's details.

        Parameters
        ----------
        request : Request
            The HTTP request containing updated user data.

        Returns
        -------
        Response
            A response with the updated user data or errors.
        """
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
        """
        Deletes a user by ID.

        Parameters
        ----------
        request : Request
            The HTTP request containing the user ID to delete.

        Returns
        -------
        Response
            A response with the remaining users after deletion.
        """
        user = User.objects.get(id=request.data["id"])
        user.delete()
        all_users = UserSerializer(User.objects.all(), many=True).data
        return Response(all_users, status=201)
    
    def post(self, request):
        """
        Creates a new user.

        Parameters
        ----------
        request : Request
            The HTTP request containing user data.

        Returns
        -------
        Response
            A response with the created user data or errors.
        """
        serializer = NewUserSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            all_users = UserSerializer(User.objects.all(), many=True).data
            return Response(all_users, status=201)
        else:
            return Response(serializer.errors, status=400)


class UserDetail(generics.RetrieveUpdateDestroyAPIView):
    """
    View for retrieving, updating, or deleting a specific user.

    Attributes
    ----------
    queryset : QuerySet
        The queryset containing all User instances.
    serializer_class : Serializer
        The serializer class for serializing and deserializing User instances.
    permission_classes : list
        Permissions required to access the view.
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsOwnerOAdmin]



class CategoryViewSet(generics.ListCreateAPIView):
    """
    ViewSet for managing categories.

    Attributes
    ----------
    queryset : QuerySet
        The queryset containing all Category instances.
    serializer_class : Serializer
        The serializer class for serializing and deserializing Category instances.
    permission_classes : list
        Permissions required to access the view.

    Methods
    -------
    get(request)
        Retrieves all categories.
    """
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [IsAuthenticated]

    def get(self, request):
        """
        Retrieves all categories.

        Parameters
        ----------
        request : Request
            The HTTP request.

        Returns
        -------
        Response
            A response containing serialized category data.
        """
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    