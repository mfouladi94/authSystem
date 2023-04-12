import json
import random

from django.contrib.auth import authenticate
from django.shortcuts import render

from rest_framework.authtoken.models import Token
from rest_framework import status
from rest_framework.authtoken.serializers import AuthTokenSerializer
from rest_framework.decorators import api_view
from rest_framework.response import Response

from useraccount.models import *
from .services.authService import *


@api_view(['POST'])
def login(request):
    data = json.loads(request.body)

    # mobile pattern 09123456789
    if "mobile" not in data or len(data["mobile"].strip()) != 11 or "code" not in data:
        return Response({"code": 10009, "error": "Not valid parameters"}, status=status.HTTP_400_BAD_REQUEST)

    return auth_mobile(data, request)
