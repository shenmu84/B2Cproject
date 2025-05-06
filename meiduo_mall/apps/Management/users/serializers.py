# forms.py 或 serializers.py
from rest_framework import serializers
from .models import UmsMenu
#接受前端传来的参数
class UmsAdminLoginParamSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=100)
    password = serializers.CharField(max_length=100)

class UmsMenuNodeSerializer(serializers.ModelSerializer):
    children = serializers.ListSerializer(child=serializers.ModelSerializer())

    class Meta:
        model = UmsMenu
        fields = ['id', 'parent_id', 'title', 'level', 'sort', 'name', 'icon', 'hidden', 'children']

class UmsAdminParamSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=100)
    password = serializers.CharField(max_length=100)
    icon = serializers.CharField(required=False)
    email = serializers.EmailField(required=False)
    nick_name = serializers.CharField(required=False)
    note = serializers.CharField(required=False)


class UpdateAdminPasswordParamSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=100, required=True)
    old_password = serializers.CharField(max_length=100, required=True)
    new_password = serializers.CharField(max_length=100, required=True)
