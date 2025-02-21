from django.db import models

# Create your models here.
# myapp/models.py

from django.db import models
from django.contrib.auth.models import User
import uuid


class BaseModel(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    class Meta:
        abstract = True




class Project(BaseModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=100)
    description = models.TextField(null=True, blank=True)
    authors = models.TextField()
    abstract = models.TextField()
    date_scraped = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return self.name
    

class Paper(BaseModel):
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    title = models.CharField(max_length=100)
    abstract = models.TextField()
    def __str__(self):
        return self.title
