from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from accounts.models import Account


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    
    def validate(self,attrs):
        
        data = super().validate(attrs)
        
        refresh = self.get_token(self.user)
        data['refresh'] = str(refresh)
        data['access'] = str(refresh.access_token)
        data['username'] = self.user.username
        data['name'] = self.user.name
        data['email'] = self.user.email

        return data
    
class AccountSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    is_active = serializers.BooleanField(read_only=True)
    class Meta:
        model = Account
        fields = (
            'id', 
            'username', 
            'email', 
            'password', 
            'name', 
            'phone',
            'date_joined',
            'is_active',
            'address',
        )
        extra_kwargs = {'password': {'write_only': True}}
        
    def create(self, validated_data):
        password = validated_data.pop('password', None)
        instance = self.Meta.model(**validated_data)
        if password is not None:
            instance.set_password(password)
        instance.is_active = True
        instance.save()
        return instance
        

class AccountUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Account
        fields = (
            'username', 
            'name', 
            'phone',
            'address',
        )


class VerifyOTPSerializer(serializers.Serializer):
    email = serializers.EmailField()
    otp = serializers.CharField()
    
        


