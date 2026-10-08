from rest_framework import serializers
from .models import User
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes

class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    confirm_password = serializers.CharField(write_only=True)
    username = serializers.CharField(read_only=True)
    total_points = serializers.IntegerField(read_only=True)
    
    class Meta:
        model = User
        fields = ['id','username','full_name','email','password','confirm_password','total_points']
    
    def validate(self, attrs):
        if attrs['password'] != attrs['confirm_password']:
            raise serializers.ValidationError(
                {"confirm_password": "Passwords do not match."}
            )
        return attrs
    
    def create(self, validated_data):
        password = validated_data.pop('password')
        validated_data.pop('confirm_password')
        user = User.objects.create(**validated_data)
        user.set_password(password)
        user.username = user.full_name.split()[0]
        user.save()
        return user  


class ForgetPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField()

    def validate_email(self, value):       # نتأكد الايميل موجود
        try:
            self.user = User.objects.get(email=value)
        except User.DoesNotExist:
            self.user = None
        return value

    def create(self, validated_data): 
        user = self.user
        if user is None:
            return None
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        token = default_token_generator.make_token(user)
        reset_token = f"{uid}-{token}"
        return { "token": reset_token }


class ResetPasswordSerializer(serializers.Serializer):
    token = serializers.CharField()
    new_password = serializers.CharField()
    confirm_password = serializers.CharField()

    def validate(self, attrs):
        token = attrs.get('token')
        new_password = attrs.get('new_password')
        confirm_password = attrs.get('confirm_password')
        if new_password != confirm_password:
            raise serializers.ValidationError(
                {"confirm_password": "Passwords do not match."}
            )
        try:
            uid, reset_token = token.split("-", 1)
            user_id = urlsafe_base64_decode(uid).decode()
            user = User.objects.get(pk=user_id)
        except (ValueError, TypeError, User.DoesNotExist):
            raise serializers.ValidationError(
                {"token": "Invalid token"}
            )
        if not default_token_generator.check_token(user,reset_token):
            raise serializers.ValidationError(
                {"token": "Invalid or expired token"}
            )
        attrs['user'] = user
        return attrs

    def create(self, validated_data):
        user = validated_data['user']
        new_password = validated_data['new_password']
        user.set_password(new_password)
        user.save()
        return user   


class UpdateProfileSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ['full_name', 'email']


class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(write_only=True)
    new_password = serializers.CharField(write_only=True)
    confirm_password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        user = self.context['request'].user
        if not user.check_password(attrs['old_password']):
            raise serializers.ValidationError(
                {"old_password": "Old password is incorrect."}
            )
        if attrs['new_password'] != attrs['confirm_password']:
            raise serializers.ValidationError(
                {"confirm_password": "Passwords do not match."}
            )
        
        return attrs