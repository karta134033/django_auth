from django.contrib.auth.models import User, Group
from .models import CustomUser
from rest_framework import viewsets
from rest_framework import permissions
from rest_framework.response import Response
from .serializers import CustomUserSerializer, UserSerializer, GroupSerializer
from rest_framework.decorators import api_view, action
from rest_framework.authtoken.models import Token
from rest_framework.authentication import TokenAuthentication
from .authentication import CustomAuthentication
import hashlib
import base64
from datetime import datetime, timedelta

class CustomUserViewSet(viewsets.ModelViewSet):
    queryset = CustomUser.objects.all()
    serializer_class = CustomUserSerializer

    @action(detail=False, methods=['post'])
    def get_user(self, request, *args, **kwargs):
        response = {}
        username = request.data['username']
        password = request.data['password']
        try:
            queryset = CustomUser.objects.get(
                username=username, password=password)
            today = str(datetime.today().strftime('%Y-%m-%d'))
            token_md5 = hashlib.md5()
            token_md5.update(
                (username + password + today).encode('utf-8'))  # 設定token
            response['status'] = True
            response['token'] = token_md5.hexdigest()
            response['uid'] = base64.b64encode(str(queryset.id).encode('utf-8'))
            response['username'] = queryset.username
            response['msg'] = '登入成功'
            return Response(response)
        except:
            response = {}
            response['status'] = False
            response['msg'] = '帳號不存在或密碼錯誤'
            return Response(response)


class UserViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    queryset = User.objects.all().order_by('-date_joined')
    serializer_class = UserSerializer
    # permission_classes = [permissions.IsAuthenticated]

    @action(detail=False, methods=['post'])
    def get_token(self, request, *args, **kwargs):
        username = request.data['user']
        try:
            queryset = User.objects.get(username=username)
        except:
            return Response('')

        try:
            token = Token.objects.get(user_id=queryset.id)
            print('Token.Exist: ', token.key)
        except Token.DoesNotExist:
            token = Token.objects.create(user=queryset)
            print('Token.DoesNotExist: ', token.key)
        return Response(token.key)

from .authentication import CustomAuthentication

class GroupViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows groups to be viewed or edited.
    """
    queryset = Group.objects.all()
    serializer_class = GroupSerializer
    authentication_classes = [CustomAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    @action(detail=False, methods=['get'])
    def get_groups(self, request, *args, **kwargs):
        queryset = Group.objects.values()
        return Response(queryset)