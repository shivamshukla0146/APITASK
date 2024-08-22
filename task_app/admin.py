from django.contrib import admin
from .models import Task

@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ('title', 'list_members', 'due_date', 'status', 'created_by')

    def list_members(self, obj):
        # Joins the usernames of all members into a single string
        return ", ".join([member.username for member in obj.members.all()])
    list_members.short_description = 'Members'
