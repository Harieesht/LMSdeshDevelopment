from django.db import models
from userauths.models import User,Profile
from django.utils.text import slugify
from shortuuid.django_fields import ShortUUIDField
from django.utils import timezone
from moviepy.editor import VideoFileClip
import math

LANGUAGE= (
    ["English","English"],
    ["Tamil","Tamil"],
    ["Malayalam","Malayalam"],
)

LEVEL=(
    ["BEGINNER","BEGINNER"],
    ["INTERMEDIATE","INTERMEDIATE"],
    ["ADVANCED","ADVANCED"],
)

TEACHER_STATUS=(
    ["DRAFT","DRAFT"],
    ["DISABLED","DISABLED"],
    ["PUBLISHED","PUBLISHED"],
)

PLATFORM_STATUS=(
    ["REVIEW","REVIEW"],
    ["DISABLED","DISABLED"],
    ["REJECTED","REJECTED"],
    ["DRAFT","DRAFT"],
    ["PUBLISHED","PUBLISHED"],
)





class Teacher(models.Model):
    user = models.OneToOneField(User,on_delete=models.CASCADE)
    image=models.FileField(upload_to='course-file',blank=True,null=True,default="default.jpg")
    full_name=models.CharField(max_length=100)
    bio =models.TextField(null=True,blank=True)
    facebook=models.URLField(null=True,blank=True)
    twitter=models.URLField(null=True,blank=True)
    about=models.TextField(null=True,blank=True)
    country = models.CharField(max_length=100,null=True,blank=True)
    
    def __str__(self):
        self.full_name
    
    def student(self):
        return CartOrderItem.objects.filter(teacher=self)   
    
    def course(self):
        return Course.objects.filter(teacher=self)
    
    def reviews(self):
        return Course.objects.filter(teacher=self).count()
    
    
class Category(models.Model):
    title=models.CharField(max_length=40)
    image=models.FileField(upload_to='course-file',default='category.jpg',null=True,blank=True)
    slug=models.SlugField(unique=True,null=True,blank=True)
    
    class Meta:
        verbose_name_plural = "Category"
        ordering = ['title']
        
    def __str__(self):
        self.title

    def course_count(self):
        return Course.objects.filter(category=self).count()
    
    def save(self,*args,**kwargs):
        if self.slug == "" or self.slug == None:
            self.slug= slugify(self.title)
        
        super(Category,self).save(*args,**kwargs)
        
        
class Course(models.Model):
    category=models.ForeignKey(Category,on_delete=models.SET_NULL,null=True,blank=True)
    teacher=models.ForeignKey(Teacher,on_delete=models.CASCADE)
    file=models.FileField(upload_to='course-file',blank=True,null=True)
    image=models.FileField(upload_to='course-file',blank=True,null=True)
    title = models.CharField(max_length=200)
    description=models.TextField(null=True,blank=True)
    price=models.DecimalField(max_digits=12,decimal_places=2,default=0.00)
    language=models.CharField(choices=LANGUAGE,default='English',max_length=200)
    level=models.CharField(choices=LEVEL,default='BEGINNER',max_length=100)
    platform_status=models.CharField(choices=PLATFORM_STATUS,default='PUBLISHED',max_length=100)
    teacher_course_status=models.CharField(choices=TEACHER_STATUS,default='PUBLISHED',max_length=100)    
    featured=models.BooleanField(default=False)
    course_id = ShortUUIDField(unique=True,length=6,max_length=20,alphabet='1234567890')
    slug=models.SlugField(unique=True,null=True,blank=True)
    date=models.DateTimeField(default=timezone.now)
    
    def  __str__(self):
        return self.title
    
    
    def save(self,*args,**kwargs):
        if self.slug == "" or self.slug == None:
            self.slug= slugify(self.title)
        
        super(Course,self).save(*args,**kwargs)
        
    def student(self):
        return EnrolledCourse.objects.filter(course=self)
    
    def curriculum(self):
        return VariantItem.objects.filter(variant__courses=self)
    
    def lectures(self):
       return VariantItem.objects.filter(variant__courses=self)
   
    def average_rating(self):
        average_rating = Review.objects.filter(course=self,active=True).aggregate(avg_rating=models.Avg('rating'))
        return average_rating['avg_rating']
    
    def rating_count(self):
        return Review.objects.filter(course=self,active=True).count()
    
    def reviews(self):
        return Review.objects.filter(course=self,active=True)
    
    
class Variant(models.Model):
    course=models.ForeignKey(Course,on_delete=models.CASCADE)
    title=models.CharField(max_length=100)
    variant_id=ShortUUIDField(unique=True,length=6,max_length=20,alphabet='1234567890')
    date=models.DateTimeField(default=timezone.now)
    
    def __str__(self):
        return self.title
    
    def variant_items(self):
        return VariantItem.objects.filter(variant=self)
    
class VariantItem(models.Model):
    variant=models.ForeignKey(Variant,on_delete=models.CASCADE,related_name='variant_items')
    title=models.CharField(max_length=100)
    description=models.TextField(null=True,blank=True)
    file=models.FileField(upload='course-file')
    duration=models.DurationField(null=True,blank=True)
    content_duration=models.CharField(max_length=1000,null=True,blank=True)
    preview=models.BooleanField(default=False)
    variant_item_id=ShortUUIDField(unique=True,length=6,max_length=20,alphabet='1234567890')
    date=models.DateTimeField(default=timezone.now)
    
    def __str__(self):
        return f"{self.variant.title}-{self.title}"
    
    def save(self,*args,**kwargs):
        super().save(*args,**kwargs)
        if self.file:
            clip=VideoFileClip(self.file.path)
            duration_seconds=clip.duration
            
            minutes,remainder=divmod(duration_seconds,60)
            minutes=math.floor(minutes)
            seconds=math.floor(remainder)

            duration_text= f"{minutes}m {seconds}s"
            self.content_duration=duration_text
            super().save(update_fields=['content_duration'])
            
class Question_Answer(models.Model):
    course=models.ForeignKey(Course,on_delete=models.CASCADE)
    user=models.ForeignKey(User,on_delete=models.SET_NULL,null=True,blank=True)
    title=models.CharField(max_length=1000,null=True,blank=True)
    qa_id=ShortUUIDField(unique=True,length=6,max_length=20,alphabet='1234567890')
    date=models.DateTimeField(default=timezone.now)
    
    def __str__(self):
        return f"{self.user.username}-{self.course.title}"
    class Meta:
        ordering=['-data']
        
    def messages(self):
        return Question_Answer_Message.objects.filter(question=self)
    
    def profile(self):
        return Profile.objects.get(user=self.user)
    
    
class Question_Answer_Message(models.Model):
    course=models.ForeignKey(Course,on_delete=models.CASCADE)
    user=models.ForeignKey(User,on_delete=models.CASCADE)
    question=models.ForeignKey(Question_Answer,on_delete=models.SET_NULL,null=True,blank=True)
    message=models.TextField(null=True,blank=True)
    qam_id=ShortUUIDField(unique=True,length=6,max_length=20,alphabet='1234567890')
    date=models.DateTimeField(default=timezone.now)
    
    
    def __str__(self):
        return f"{self.user.username}-{self.course.title}"
    class Meta:
        ordering=['data']
        
    def profile(self):
        return Profile.objects.get(user=self.user)
    
    
class Cart(models.Model):
    course=models.ForeignKey(Course,on_delete=models.CASCADE)
    user=models.ForeignKey(User,on_delete=models.CASCADE)
    price=models.DecimalField(max_digit=12,default=0.00,decimal_places=2)
    tax_fee=models.DecimalField(max_digit=12,default=0.00,decimal_places=2)
    total=models.DecimalField(max_digit=12,default=0.00,decimal_places=2)
    country=models.CharField(max_length=100m,null=True,blank=True,default="India")
    cart_id=ShortUUIDField(unique=True,length=6,max_length=20,alphabet='1234567890')
    date=models.DateTimeField(default=timezone.now)
    
    def __str__(self):
        return self.course.title

class CartOrder(models.Model):
    student=models.ForeignKey(User,on_delete=models.SET_NULL,null=True,blank=True)
    teacher
    
    
    
    
            
            
    
    
        
    
    
    
          
    
    
    
    
    
    
        
    
    
    
    
     