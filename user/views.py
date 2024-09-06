from django.contrib.auth import authenticate
from django.contrib.auth import login as auth_login
from django.template.loader import render_to_string
from rest_framework import status
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.response import Response
from rest_framework.views import APIView

import random
from .models import ActiveCode
from django.contrib.auth.models import User
from django.core.mail import EmailMessage

from django.contrib.auth import logout as auth_logout

from rest_framework.authentication import SessionAuthentication
from rest_framework.authtoken.models import Token

from .serializers import UserSerializer


def send_activation_email(user, code):
    mail_subject = 'Blog Account Activation'
    message = render_to_string('acc_active_email.html', {
        'user': user,
        'code': code,
    })
    email = EmailMessage(
        mail_subject, message, to=[user.email], from_email="info@azizinasim.ir",
    )
    email.send()


# disable CSRF checking
class CsrfExemptSessionAuthentication(SessionAuthentication):

    def enforce_csrf(self, request):
        return  # To not perform the csrf check previously happening


# user registration view
class RegistrationView(APIView):
    def post(self, request):
        username = request.POST.get("username")
        password = request.POST.get("password")
        email = request.POST.get("email")
        user = User.objects.create_user(email=email, username=username, password=password)
        user.is_active = False
        user.save()
        code = random.randint(100000, 999999)
        ActiveCode.objects.create(user=user, code=code)
        send_activation_email(user, code)
        return Response('email sent', status=status.HTTP_200_OK)


class ActivationView(APIView):
    def post(self, request):
        cd = {
            "username": request.POST.get("username"),
            "email": request.POST.get("email"),
            "code": request.POST.get("code")
        }
        try:
            user = User.objects.get(username=cd["username"], email=cd["email"])
            code = ActiveCode.objects.get(user=user)
            if user is not None and code.code == cd["code"]:
                user.is_active = True
                user.save()
                auth_login(request, user)
                return Response('successful', status=status.HTTP_200_OK)
            else:
                return Response('invalid', status=status.HTTP_400_BAD_REQUEST)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            return Response("unknown user", status=status.HTTP_400_BAD_REQUEST)


# user login view
class LoginView(APIView):
    # authentication_classes = (CsrfExemptSessionAuthentication, TokenAuthentication)
    parser_classes = [FormParser, MultiPartParser]

    def post(self, request):
        cd = {
            "username": request.POST.get("username"),
            "password": request.POST.get("password")
        }
        print(f"username: {cd['username']}\n password: {cd['password']}")
        user = User.objects.get(username=cd["username"])
        if user.check_password(cd["password"]):
            token, created = Token.objects.get_or_create(user=user)
            if user is not None:
                if user.is_active:
                    print("ok")
                    return Response({"token": token.key}, status=status.HTTP_200_OK)
        return Response("failed", status=status.HTTP_400_BAD_REQUEST)


class ResndEmailView(APIView):
    def post(self, request):
        username = request.POST.get("username")
        email = request.POST.get("email")
        user = User.objects.get(username=username, email=email)
        code = ActiveCode.objects.get(user=user)
        send_activation_email(user, code.code)
        return Response("email send", status=status.HTTP_200_OK)


class ChangePassword(APIView):
    def post(self, request):
        username = request.POST.get("username")
        password = request.POST.get("password")
        new_password = request.POST.get("new_password")
        user = User.objects.get(username=username)
        if user.check_password(password):
            user.set_password(new_password)
            user.save()
            return Response("password has changed", status=status.HTTP_200_OK)
        return Response("wrong password", status=status.HTTP_400_BAD_REQUEST)


class ProfileView(APIView):
    def get(self, request):
        if request.user.is_authenticated:
            user = request.user
            serializer = UserSerializer(user)
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response("You are not logged in", status=status.HTTP_401_UNAUTHORIZED)


class GetUsername(APIView):
    def get(self, request):
        user = request.user
        print(user.username)
        if user is not None:
            return Response({"username": user.username}, status=status.HTTP_200_OK)
        return Response({"username": "not login"}, status=status.HTTP_200_OK)
