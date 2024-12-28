from django.shortcuts import get_object_or_404
from django.contrib.auth import get_user_model
from task_data_app.models import User
from joinbackend.settings import AUTH_USER_MODEL

def authenticate_with_username_and_password(email, password):
    """
    Authenticates a user using their email and password.

    Parameters
    ----------
    email : str
        The email address of the user attempting to log in.
    password : str
        The password provided for authentication.

    Returns
    -------
    User or None
        The authenticated user if the credentials are valid; otherwise, None.

    Notes
    -----
    - If the email does not exist or the password is incorrect, None is returned.
    - Uses `get_object_or_404` to fetch the user instance by email.
    """
    user = User
    try:
        user = get_object_or_404(user, email=email)
        if user.check_password(password):
            return user
    except user.DoesNotExist:
        return None