from django.contrib import admin
from .models import Todo

# to display the created date from the todo Model
class TodoAdmin(admin.ModelAdmin):
    readonly_fields = ('created',)

# Register your models here.
admin.site.register(Todo, TodoAdmin)