# Join Backend

## A Django-based backend Example Project for managing tasks, users, categories, and subtasks. It provides RESTful API endpoints for CRUD operations and user authentication, supporting a task management application.


This project is build as a student project to create an costum REST API with Django Rest Framework. It contains custom permission classes and custom serializer classes. It belong on side with the Join Frontend. 

* Create create serializer classes
* Create an REST API for Kanban Board

## How to install this BackEnd

1. clone this project
```
    git clone https://github.com/your-repo/joinbackend.git
```
2. Create a virtual enviroment:
```
    python -m venv env
```

3. install dependencies:
```
    pip install -r requirements.txt
```

4. Apply migrations:
```
    python manage.py makemigrations
    python manage.py migrate
```

5. Create a superuser
```
    python manage.py createsuperuser
```

6. Start the development server
```
    python manage.py runserver
```

