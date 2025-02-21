# myapp/serializers.py
from rest_framework import serializers
from .models import *

class ProjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Project
        fields = ['name', 'description', 'created_at', 'updated_at']


class ResearchPaperSerializer(serializers.ModelSerializer):
    class Meta:
        model = Paper
        fields = ['title', 'authors', 'abstract']