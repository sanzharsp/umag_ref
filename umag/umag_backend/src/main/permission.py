from rest_framework import permissions
from dotenv import load_dotenv
import os
load_dotenv()
class HasAPIKey(permissions.BasePermission):
    def has_permission(self, request, view):
        api_key = request.headers.get('Authorization')
        if api_key and api_key == os.getenv('PERMISSION_KEY'):
            return True
        return False