from django.urls import path, include
from .views import TaskViewSet, UserViewSet, CategoryViewSet, UserDetail, RegistrationView, CustomLoginView, TaskSummaryView, AuthenticationView
urlpatterns = [
    path('task/', TaskViewSet.as_view(), name='task_list'),
    path('task/summary/', TaskSummaryView.as_view(), name='task_summary'),
    path('user/', UserViewSet.as_view(), name='user_list'),
    path('user/<int:pk>', UserDetail.as_view(), name='user_detail'),
    path('user/register/', RegistrationView.as_view(), name='register_user'),
    path('user/active/', AuthenticationView.as_view(), name='active_user'),
    path('user/login/', CustomLoginView.as_view(), name='login_user'),
    path('contact/', UserViewSet.as_view(), name='contact_list'),
    path('contact/new/', RegistrationView.as_view(), name='contact_detail'),
    path('category/', CategoryViewSet.as_view(), name='category_list'),
    path('api-auth/', include('rest_framework.urls', namespace='rest_framework')),
]