from django.contrib import admin
from .models import User, Task, SubTask, Category



class TaskAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'container',  'due_date', 'priority')

# Register your models here.

admin.site.register(User)
admin.site.register(Task , TaskAdmin)	
admin.site.register(SubTask)
admin.site.register(Category)


