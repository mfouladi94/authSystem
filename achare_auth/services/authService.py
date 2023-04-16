import json
import random

from django.utils import timezone
from datetime import timedelta
from django.contrib.auth import authenticate
from django.core.cache import cache
from django.shortcuts import render

from rest_framework.authtoken.models import Token

from rest_framework import status
from rest_framework.authtoken.serializers import AuthTokenSerializer
from rest_framework.decorators import api_view
from rest_framework.response import Response

from useraccount.models import *
from ..models import *


# Response code 100 == success resopnse
# Response code 102 == success resopnse  + Register sms
# Response code 104 == success resopnse  + get user data from user
# Response code 10009 == Error + message


# step 1 check user existence with phone number

# step 2 login user with phone number and password

# step 3  register user with sms code

# step 4 setting user profile data nad password


def auth_mobile(data, request):
    mobile_number = data["mobile"].strip()

    # Check if IP address is banned
    ip_address = request.META.get('REMOTE_ADDR', None)
    if is_ip_banned(ip_address):
        # IP address is banned, take appropriate action
        return Response({"code": 10009, 'error': 'درحال حاضر امکان تراکنش برای شما وجود ندارد '},
                        status=status.HTTP_400_BAD_REQUEST)

    # step 1 check user existence with phone number
    if data["code"] == 1:

        userprofile = UserProfile.objects.filter(mobile_number=mobile_number).first()
        ft = generate_flow_token(mobile_number)
        # Register the user
        if not check_user_is_registered_successfully(mobile_number):
            return Response({"code": 102, "flowToken": ft.code, "error": "",
                             "message": "ثبت نام شما انجام شد و کد برای شما ارسال شد "},
                            status=status.HTTP_200_OK)

        return Response({"code": 100, "flowToken": ft.code, "error": "", "message": "کلمه عبور خود را وارد کنید "},
                        status=status.HTTP_200_OK)
    # step 2 login user with phone number and password
    elif data["code"] == 2:

        if "password" not in data or len(data["password"]) >= 30:
            return Response({"code": 10009, "error": "Not valid parameters"}, status=status.HTTP_400_BAD_REQUEST)

        flow_token = get_flow_token(data["flowToken"], mobile_number)
        if not flow_token:
            return Response({"code": 10009, 'error': 'flow token is required'},
                            status=status.HTTP_400_BAD_REQUEST)

        # Register the user
        if not check_user_is_registered_successfully(mobile_number):
            return Response({"code": 102, "error": "", "message": "ثبت نام شما انجام شد و کد برای شما ارسال شد "},
                            status=status.HTTP_200_OK)

        userprofile = UserProfile.objects.filter(mobile_number=mobile_number).first()

        # this can be replaced with JWT

        serializer = AuthTokenSerializer(data={'username': userprofile.user.username, 'password': data["password"]})

        if serializer.is_valid():
            user = userprofile.user
            token, created = Token.objects.get_or_create(user=user)  # Get or create token for user
            return Response({"code": 100, 'token': token.key},
                            status=status.HTTP_201_CREATED)  # Return token as response
        else:
            handle_failed_login_attempt(request, userprofile.user.username)
            return Response({"code": 10009, 'error': 'Invalid username or password'},
                            status=status.HTTP_400_BAD_REQUEST)

    # step 3  register user with sms code
    elif data["code"] == 3:

        if "smsToken" not in data or len(data["smsToken"]) != 6:
            return Response({"code": 10009, "error": "Not valid parameters"}, status=status.HTTP_400_BAD_REQUEST)

        flow_token = get_flow_token(data["flowToken"], mobile_number)
        if not flow_token:
            return Response({"code": 10009, 'error': 'flow token is required'},
                            status=status.HTTP_400_BAD_REQUEST)

        userprofile = UserProfile.objects.filter(mobile_number=mobile_number).first()

        if read_sms_token(mobile_number) != data["smsToken"]:
            # Register the user
            if not check_user_is_registered_successfully(mobile_number):

                handle_failed_login_attempt(request, userprofile.user.username)

                return Response({"code": 10009, "error": "کد وارد شده صحیح نیست مجدد کد ارسال شد"},
                                status=status.HTTP_400_BAD_REQUEST)

        userprofile = UserProfile.objects.filter(mobile_number=mobile_number).first()
        userprofile.is_register_auth_completed = True
        userprofile.save()

        flow_token.is_verified = True
        flow_token.save()

        if not userprofile.is_register_data_completed:
            return Response({"code": 104, "error": "", "message": "مشخصات کاربری خود را وارد کنید "},
                            status=status.HTTP_200_OK)

        else:
            # login user
            return Response({"code": 100, "error": "", "message": "کلمه عبور خود را وارد کنید "},
                            status=status.HTTP_200_OK)
    # step 4 setting user profile data nad password
    elif data["code"] == 4:
        if "u_name" not in data or "u_family" not in data or "u_email" not in data or "password" not in data:
            return Response({"code": 10009, "error": "Not valid parameters"}, status=status.HTTP_400_BAD_REQUEST)

        flow_token = get_flow_token(data["flowToken"], mobile_number)
        if not flow_token:
            return Response({"code": 10009, 'error': 'flow token is required'},
                            status=status.HTTP_400_BAD_REQUEST)

        if not flow_token.is_verified:
            return Response({"code": 10009, 'error': 'اعتبار سنجی پیامکی انجام نشده است . لطفا دوباره تلاش کنید'},
                            status=status.HTTP_400_BAD_REQUEST)

        userprofile = UserProfile.objects.filter(mobile_number=mobile_number).first()

        if not userprofile.is_register_auth_completed or not userprofile:
            # Register the user
            if not check_user_is_registered_successfully(mobile_number):
                return Response({"code": 10009, "error": "کد وارد شده صحیح نیست مجدد ارسال شد"},
                                status=status.HTTP_400_BAD_REQUEST)

        userprofile.user.first_name = data["u_name"]
        userprofile.user.last_name = data["u_family"]
        userprofile.user.email = data["u_email"]
        userprofile.user.set_password(data["password"])

        userprofile.user.save()
        userprofile.save()
        data = {'username': str(userprofile.user.username), 'password': data["password"]}
        print(data)
        serializer = AuthTokenSerializer(
            data={'username': str(userprofile.user.username), 'password': data["password"]})

        if serializer.is_valid():
            user = userprofile.user
            token, created = Token.objects.get_or_create(user=user)  # Get or create token for user
            return Response({"code": 100, 'token': token.key},
                            status=status.HTTP_201_CREATED)  # Return token as response
        else:
            return Response({"code": 10009, 'error': 'Invalid username or password', 'errors': serializer.errors},
                            status=status.HTTP_400_BAD_REQUEST)


def handle_failed_login_attempt(request, username):
    ip_address = request.META.get('REMOTE_ADDR', None)
    failed_login_attempt = FailedLoginAttempt.objects.create(ip_address=ip_address, username=username)
    failed_login_attempt.save()


def is_ip_banned(ip_address):
    now = timezone.now()
    time_threshold = now - timedelta(hours=1)  # 1 hour ago
    failed_attempts = FailedLoginAttempt.objects.filter(ip_address=ip_address, timestamp__gte=time_threshold)
    return failed_attempts.count() >= 3



# Generate an SMS token
def generate_sms_token():
    # Generate a random 6-digit number
    sms_token = str(random.randint(100000, 999999))
    print("SMS TOKEN", sms_token)
    return sms_token


# Write SMS token to LocMemCache
def write_sms_token(phone_number, sms_token):
    # Store the SMS token in the cache with the phone number as the key
    cache.set(phone_number, sms_token)


# Read SMS token from LocMemCache
def read_sms_token(phone_number):
    # Retrieve the SMS token from the cache using the phone number as the key
    sms_token = cache.get(phone_number)
    return sms_token


def check_user_is_registered_successfully(mobile_number):
    userprofile = UserProfile.objects.filter(mobile_number=mobile_number).first()

    # Register the user
    if not userprofile:
        user = User.objects.create_user("user_" + mobile_number, )
        user.save()

        user_profile = UserProfile.objects.create(user=user,
                                                  mobile_number=mobile_number.strip())
        user_profile.save()
        # create temp sms token
        sms_token = generate_sms_token()
        write_sms_token(mobile_number, sms_token)

        return False

    if not userprofile.is_register_auth_completed:
        # create temp sms token
        sms_token = generate_sms_token()
        write_sms_token(mobile_number, sms_token)

        return False

    return True


def generate_flow_token(mobile_number):
    flowToken = FlowToken.objects.create(mobile_number=mobile_number)
    flowToken.save()
    return flowToken


def get_flow_token(flowtoenId, mobile):
    flowToken = FlowToken.objects.filter(code=flowtoenId, mobile_number=mobile).first()
    return flowToken
