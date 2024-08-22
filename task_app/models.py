from django.db import models
from django.contrib.auth.models import User

class Task(models.Model):
    STATUS_CHOICES = (
        ('todo', 'To Do'),
        ('inprogress', 'In Progress'),
        ('done', 'Done')
    )
    
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    due_date = models.DateTimeField()
    status = models.CharField(max_length=12, choices=STATUS_CHOICES, default='todo')
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='tasks')
    members = models.ManyToManyField(User, related_name='task_members')

    def __str__(self):
        return self.title
