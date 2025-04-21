from django.shortcuts import render
from .serializers import UserSerializer
from .models import MyUser as User
from rest_framework.response import Response
from rest_framework.decorators import api_view


@api_view(['GET'])
def user_list(request, ):
    users = User.objects.all().order_by('username').exclude(username=request.user)
    serializer = UserSerializer(instance=users, many=True)
    return Response(serializer.data)


@api_view(['GET'])
def user_by_username(request, username, ):
    try:
        user = User.objects.get(username=username)
    except User.DoesNotExist:
        return Response({'message': 'User doesn`t exist.'})
    serializer = UserSerializer(instance=user)
    return Response(serializer.data)
