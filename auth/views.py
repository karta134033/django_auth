from django.contrib.auth.models import User, Group
from rest_framework import viewsets
from rest_framework import permissions
from rest_framework.response import Response
from auth.serializers import UserSerializer, GroupSerializer
from rest_framework.decorators import api_view, action
from rest_framework.authtoken.models import Token
from rest_framework.authentication import TokenAuthentication


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

class GroupViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows groups to be viewed or edited.
    """
    queryset = Group.objects.all()
    serializer_class = GroupSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]