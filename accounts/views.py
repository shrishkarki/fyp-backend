import jwt
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework.decorators import permission_classes
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView

import random

from .serializers import (
    AccountSerializer, 
    CustomTokenObtainPairSerializer, 
    VerifyOTPSerializer,
    AccountUpdateSerializer
)
from .models import Account
from .utils import Util

class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer

@permission_classes((AllowAny,))
class RegisterView(APIView):
    def post(self, request):   
        serializer = AccountSerializer(data=request.data)
        serializer.is_valid(raise_exception=True) 
        serializer.save()       

        account = serializer.instance        

        # otp = random.randint(100000, 999999) 
        
        # # Send otp to email
        # Util.send_otp_vai_email(otp,account.email)
        # account.otp = otp
        # account.save()

        
        return Response(serializer.data, status=201)



class SendRegisterOTP(APIView):
    def get(self, request):
        email = request.GET.get('email')
        try:
            account = Account.objects.get(email=email)
        except Account.DoesNotExist:
            return Response({'error':"Account does not exist"},status=400)
            
        if account.is_active:
            return Response({'error':'Account is already active'},status=400)
        
        # generate random 6 digit otp and send it to email
        otp = random.randint(100000, 999999)
        Util.send_otp_vai_email(otp,email)

        # save otp in account
        account.otp = otp        
        account.save()

        return Response({'success':'OTP sent to your email'},status=200)


class VerifyRegisterOTP(APIView):
    def post(self, request):
        data = request.data
        serializer = VerifyOTPSerializer(data=data)
        serializer.is_valid(raise_exception=True)

        email = serializer.validated_data['email']
        otp = serializer.validated_data['otp']

        try:
            account = Account.objects.get(email=email)
        except Account.DoesNotExist:
            return Response({'error':'Account does not exist'},status=400)

        if account.is_active:
            return Response({'error':"Account already verified"},status=400)
            
        if account.otp == otp:
            account.is_active = True
            account.save()
            return Response({
                'success':'Account verified successfully',
                'token':str(RefreshToken.for_user(account).access_token),
                'username':account.username,
                'name':account.name,
                'email':account.email,
            },status=200)

        return Response({'error':'Invalid OTP'},status=400)
              
class SendResetPasswordOTP(APIView):
    def get(self, request):
        email = request.GET.get('email')
        try:
            account = Account.objects.get(email=email)
        except Account.DoesNotExist:
            return Response({'error':"Account does not exist"},status=400)
        
        # generate random 6 digit otp and send it to email
        otp = random.randint(100000, 999999)
        Util.send_otp_vai_email(otp,email)

        # save otp in account
        account.otp = otp        
        account.save()

        return Response({'success':'OTP sent to your email'},status=200)

class VerifyResetPasswordOTP(APIView):
    def post(self, request):
        data = request.data
        serializer = VerifyOTPSerializer(data=data)
        serializer.is_valid(raise_exception=True)

        email = serializer.validated_data['email']
        otp = serializer.validated_data['otp']

        try:
            account = Account.objects.get(email=email)
        except Account.DoesNotExist:
            return Response({'error':'Account does not exist'},status=400)

        if account.otp == otp:
            return Response({
                'success':'OTP verified successfully',
                'token': Util.jwt_encode({"email":email,'otp':otp}),
            },status=200)

        return Response({'error':'Invalid OTP'},status=400)

class ResetPasswordView(APIView):
    def post(self, request):
        # get token from the request data
        token = request.data.get('token')
        try:
            data = Util.jwt_decode(token)
        except jwt.ExpiredSignatureError:
            return Response({'error':'Token expired'},status=400)
        except jwt.DecodeError:
            return Response({'error':'Invalid token'},status=400)
            
        email = data['email']
        otp = data['otp']

        # checking if the otp is correct
        try:
            account = Account.objects.get(email=email)
            otp == account.otp
        except :
            return Response({'error':'Something Went Wrong!!'},status=400)

        # resetting password
        password = request.data.get('password')

        account.set_password(password)
        account.save()

        return Response({'success':'Password reset successfully'},status=200)
    

class AccountDetailView(APIView):
    def get(self, request, username):
        try:
            account = Account.objects.get(username=username)
        except Account.DoesNotExist:
            return Response({'error':'Account does not exist'},status=400)
        serializer = AccountSerializer(account)
        return Response(serializer.data)

    def put(self, request, username):
        account = Account.objects.get(username=username)
        serializer = AccountUpdateSerializer(account, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)