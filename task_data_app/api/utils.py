from django.shortcuts import get_object_or_404
from django.contrib.auth import get_user_model
from task_data_app.models import User
from joinbackend.settings import AUTH_USER_MODEL

def authenticate_with_username_and_password(email, password):
    user = User
    try:
        user = get_object_or_404(user, email=email)
        if user.check_password(password):
            return user
    except user.DoesNotExist:
        return None