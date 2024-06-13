from rest_framework import serializers
from userauths.models import User,Profile
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer 
from django.contrib.auth.password_validation import validate_password
from api import models as api_models

class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls,user):
        token = super().get_token(user) # getting my jwt token with user object
        
        token['full_name']=user.full_name   # adding details to my jwt token 
        token['email']=user.email
        token['username']=user.username
        
        return token  #returning jwt token
    
    
class RegisterSerializer(serializers.ModelSerializer):
    password=serializers.CharField(write_only=True,required=True,validators=[validate_password])
    password2=serializers.CharField(write_only=True,required=True)
    
    class Meta:
        model=User
        fields=['full_name','email','password','password2']
        
    def validate(self,attr):
        if attr['password'] != attr ['password2']:
            raise serializers.ValidationError({"password":"Password fields didnt match"})
        
        return attr
    
    def create(self,validated_data):
        user=User.objects.create(
            full_name=validated_data['full_name'],
            email=validated_data['email']
        )
        email_username,_=user.email.split('@')  #its a tuple
        user.username=email_username
        user.set_password(validated_data['password'])
        user.save()
        
        return user
    
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model=User
        fields=["username",'email']
        
    
    
    
    
class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model=Profile
        fields='__all__'
        
    
class CategorySerializer(serializers.ModelSerializer):
    course_count=None
    class Meta:
        model=api_models.Category
        field=['title','image','slug','course_count']
   
class TeacherSerializer(serializers.ModelSerializer):
    class Meta:
        model=api_models.Teacher
        field=[
            "user",
            "image",
            "full_name",
            "bio",
            "facebook",
            "twitter",
            "about",
            "country",
            "student",
            "course",
            "reviews",
        ]    
        
class EnrolledCourseSerializer(serializers.ModelSerializer):
    
    class Meta:
        model=api_models.EnrolledCourse
        field='__all__'

class VariantItemSerializer(serializers.ModelSerializer):
    class Meta:
        model=api_models.VariantItem
        field='__all__'
        

class VariantSerializer(serializers.ModelSerializer):
    class Meta:
        model=api_models.Variant
        field='__all__'
        

        
class Question_AnswerSerializer(serializers.ModelSerializer):
    class Meta:
        model=api_models.Question_Answer
        field='__all__'
        
class CourseSerializer(serializers.ModelSerializer):
    
    students=EnrolledCourseSerializer(many=True)
    curriculum=VariantItemSerializer(many=True)
    lectures=VariantItemSerializer(many=True)
    
    class Meta:
        model=api_models.Course
        field=[
            "category",
            "teacher",
            "file",
            "image",
            "title",
            "description",
            "price",
            "language",
            "level",
            "platform_status",
            "teacher_course_status",
            "featured",
            "course_id",
            "slug",
            "date",
            "students",
            "curriculum",
            "lectures",
            "average_rating",
            "rating_count",
            "reviews",
            
        ] 
        
        
class Question_Answer_MessageSerializer(serializers.ModelSerializer):
    class Meta:
        model=api_models.Question_Answer_Message
        field='__all__'
        
class CartSerializer(serializers.ModelSerializer):
    
    class Meta:
        model=api_models.Cart
        field='__all__' 

class CartOrderSerializer(serializers.ModelSerializer):
    
    class Meta:
        model=api_models.CartOrder
        field='__all__' 
        
class CartOrderItemSerializer(serializers.ModelSerializer):
    
    class Meta:
        model=api_models.CartOrderItem
        field='__all__' 

class CertificateSerializer(serializers.ModelSerializer):
    
    class Meta:
        model=api_models.Certificate
        field='__all__' 
        
class CompletedLessonsSerializer(serializers.ModelSerializer):
    
    class Meta:
        model=api_models.CompletedLessons
        field='__all__' 

 
        
class NoteSerializer(serializers.ModelSerializer):
    
    class Meta:
        model=api_models.Note
        field='__all__' 
        
class ReviewSerializer(serializers.ModelSerializer):
    
    class Meta:
        model=api_models.Review
        field='__all__' 
    
class NotificationSerializer(serializers.ModelSerializer):
    
    class Meta:
        model=api_models.Notification
        field='__all__' 
        
class CouponSerializer(serializers.ModelSerializer):
    
    class Meta:
        model=api_models.Coupon
        field='__all__' 
        
class WishlistSerializer(serializers.ModelSerializer):
    
    class Meta:
        model=api_models.Wishlist
        field='__all__' 
        
class CountrySerializer(serializers.ModelSerializer):
    
    class Meta:
        model=api_models.Country
        field='__all__' 
        
