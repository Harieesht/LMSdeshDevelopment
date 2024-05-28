from django.shortcuts import render
from api import serializers as api_serializer
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework import generics,status
from userauths.models import User,Profile
from rest_framework.permissions import AllowAny
from random import randint
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.response import Response
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings

class MyTokenObtainPairView(TokenObtainPairView):
    serializer_class=api_serializer.MyTokenObtainPairSerializer
    
    
class RegisterView(generics.CreateAPIView):
    queryset=User.objects.all()
    permission_classes=[AllowAny]
    serializer_class=api_serializer.RegisterSerializer


def generate_random_otp(length=7):
    otp="".join([str(randint(0,9)) for _ in range(length)])
    return otp
    
class PasswordResetEmailVerifyAPIView(generics.RetrieveAPIView):
    permission_classes=[AllowAny]
    serializer_class=api_serializer.UserSerializer
    
    def get_object(self):
        email=self.kwargs['email']  #api/password-email-verify/harirakha12@gmail.com/
        user=User.objects.filter(email=email).first()
        
        if user:
            user.otp = generate_random_otp()
            user.save()
            
            uuidb64=user.pk
            refresh = RefreshToken.for_user(user)
            refresh_token=str(refresh.access_token)
            user.refresh_token=refresh_token
            
            link = f"http://localhost:5173/create-new-password/?otp={user.otp}&uuidb64={uuidb64}&refresh_token={refresh_token}"
            
            context={
                'link':link,
                'username':user.username,
                
            }
            
            subject = "Password Reset Email"
            text_body=render_to_string("email/password_reset.txt",context)
            html_body=render_to_string("email/password_reset.html",context)
            
            send_mail(subject,html_body,settings.EMAIL_HOST_USER,[user.email])
            
        return user
    

class PasswordChangeAPIView(generics.CreateAPIView):
    permission_classes=[AllowAny]
    serializer_class=api_serializer.UserSerializer
    
    def create(self,request,*args,**kwargs):
        payload=request.data
        
        otp=payload['otp']
        uuidb64=payload['uuidb64']
        password=payload['password']
        
        
        user=User.objects.get(id=uuidb64,otp=otp)
        if user:
            user.set_password(password)
            user.otp=""
            user.save()
        
            return Response({"message":"Password is changed successfully"},status=status.HTTP_201_CREATED)
        else:
            return Response({'message':"User doesnt exist"},status=status.HTTP_404_NOT_FOUND)
        
                        
    
    
            
    