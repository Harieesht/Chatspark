from rest_framework import serializers
from .models import *


class ServerSerializer(serializers.ModelSerializer):
    class Meta:
        model=Server
        fields="__all__"