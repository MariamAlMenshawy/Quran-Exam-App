from django.shortcuts import render
from rest_framework.permissions import AllowAny,IsAuthenticated
from rest_framework.generics import CreateAPIView, RetrieveAPIView, UpdateAPIView
from .models import User
from .serializers import UserSerializer,ForgetPasswordSerializer,ResetPasswordSerializer,UpdateProfileSerializer,ChangePasswordSerializer
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.response import Response
from rest_framework import status
# Create your views here.

# POST Create New User
class Register(CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [AllowAny]

    def create(self,request,*args,**kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        refresh = RefreshToken.for_user(user)
        return Response({
            "access": str(refresh.access_token),
            "refresh": str(refresh),
        },status=status.HTTP_201_CREATED)


class ForgetPassword(CreateAPIView):
    serializer_class = ForgetPasswordSerializer
    permission_classes = [AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.save()
        return Response({
            "message": "Password reset token generated successfully",
            "token": data["token"]
        },
        status=status.HTTP_200_OK)


    
class ResetPassword(CreateAPIView):
    serializer_class = ResetPasswordSerializer
    permission_classes = [AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({
            "message": "Password reset successfully"
        },
        status=status.HTTP_200_OK)

class GetProfile(RetrieveAPIView):
    permission_classes=[IsAuthenticated]
    serializer_class = UserSerializer

    def get_object(self):
        return self.request.user


class UpdateProfile(UpdateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = UpdateProfileSerializer
    http_method_names = ['put']

    def get_object(self):
        return self.request.user

class ChangePassword(UpdateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = ChangePasswordSerializer
    http_method_names = ['put']

    def update(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        user = request.user
        user.set_password(serializer.validated_data['new_password'])
        user.save()
        return Response({"message": "Password changed successfully."},status=status.HTTP_200_OK)
   

