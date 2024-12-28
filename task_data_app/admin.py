from django.contrib import admin
from .models import User, Task, SubTask, Category

class SubTaskInline(admin.TabularInline):
    """
    Inline admin interface for SubTask.

    Attributes
    ----------
    model : SubTask
        The model represented in this inline admin.
    extra : int
        The number of empty SubTask forms displayed in the inline admin.
    """
    model = SubTask
    extra = 1


class TaskAdmin(admin.ModelAdmin):
    """
    Admin interface for the Task model.

    Attributes
    ----------
    list_display : tuple
        Fields to display in the admin list view for Task.
    inlines : list
        Inline models to include in the Task admin interface.
    """
    list_display = ('id', 'title', 'container',  'due_date', 'priority')
    inlines = [SubTaskInline]


admin.site.register(User)
admin.site.register(Task , TaskAdmin)	
admin.site.register(SubTask)
admin.site.register(Category)


