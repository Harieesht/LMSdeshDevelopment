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

PAYMENT_STATUS=(
    ["PAID","PAID"],
    ["PROCESSING","PROCESSING"],
    ["FAILED","FAILED"],
)

PLATFORM_STATUS=(
    ["REVIEW","REVIEW"],
    ["DISABLED","DISABLED"],
    ["REJECTED","REJECTED"],
    ["DRAFT","DRAFT"],
    ["PUBLISHED","PUBLISHED"],
)

RATING=(
    [1,"1 star"],
    [2,"2 star"],
    [3,"3 star"],
    [4,"4 star"],
    [5,"5 star"],
)

NOTI_TYPE=(
    ["New Order","New Order"],
    ["New Review","New Review"],
    ["New Course Question","New Course Question"],
    ["DRAFT","DRAFT"],
    ["Course Published","Course Published"],
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
    file=models.FileField(upload_to='course-file')
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
        ordering=['-date']
        
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
        ordering=['date']
        
    def profile(self):
        return Profile.objects.get(user=self.user)
    
    
class Cart(models.Model):
    course=models.ForeignKey(Course,on_delete=models.CASCADE)
    user=models.ForeignKey(User,on_delete=models.CASCADE)
    price=models.DecimalField(max_digits=12,default=0.00,decimal_places=2)
    tax_fee=models.DecimalField(max_digits=12,default=0.00,decimal_places=2)
    total=models.DecimalField(max_digits=12,default=0.00,decimal_places=2)
    country=models.CharField(max_length=100,null=True,blank=True,default="India")
    cart_id=ShortUUIDField(unique=True,length=6,max_length=20,alphabet='1234567890')
    date=models.DateTimeField(default=timezone.now)
    
    def __str__(self):
        return self.course.title

class CartOrder(models.Model):
    student=models.ForeignKey(User,on_delete=models.SET_NULL,null=True,blank=True)
    teacher=models.ManyToManyField(Teacher,blank=True)
    sub_total=models.DecimalField(max_digits=12,default=0.00,decimal_places=2)
    tax_fee=models.DecimalField(max_digits=12,default=0.00,decimal_places=2)
    total=models.DecimalField(max_digits=12,default=0.00,decimal_places=2)
    initial_total=models.DecimalField(max_digits=12,default=0.00,decimal_places=2)
    saved=models.DecimalField(max_digits=12,default=0.00,decimal_places=2)
    payment_status=models.CharField(max_length=100,choices=PAYMENT_STATUS,default="Processing")
    full_name=models.CharField(max_length=100,null=True,blank=True)
    email=models.EmailField(max_length=100,null=True,blank=True)
    country=models.CharField(max_length=100,null=True,blank=True)
    coupons=models.ManyToManyField("api.Coupon",blank=True)
    stripe_session_id=models.CharField(max_length=1000,null=True,blank=True)
    oid=ShortUUIDField(unique=True,length=6,max_length=20,alphabet='1234567890')
    date=models.DateTimeField(default=timezone.now)
    
    
    class Meta:
        ordering=['-date']
        
    def order_items(self):
        return CartOrderItem.objects.filter(order=self)
    
    def __str__(self):
        return self.oid
    
class CartOrderItem(models.Model):
    teacher=models.ForeignKey(Teacher,on_delete=models.CASCADE,related_name='orderitem')
    course=models.ForeignKey(Course,on_delete=models.CASCADE,related_name='order_item')
    order=models.ForeignKey(CartOrder,on_delete=models.CASCADE)
    tax_fee=models.DecimalField(max_digits=12,default=0.00,decimal_places=2)
    total=models.DecimalField(max_digits=12,default=0.00,decimal_places=2)
    initial_total=models.DecimalField(max_digits=12,default=0.00,decimal_places=2)
    saved=models.DecimalField(max_digits=12,default=0.00,decimal_places=2)
    coupons=models.ForeignKey("api.Coupon",on_delete=models.SET_NULL,null=True,blank=True)
    applied_coupon=models.BooleanField(default=False)
    oid=ShortUUIDField(unique=True,length=6,max_length=20,alphabet='1234567890')
    date=models.DateTimeField(default=timezone.now)
    
    class Meta:
        ordering=['-date']
        
    def order_id(self):
        return f"Order ID #{self.order.id}"
    
    def payment_status(self):
        return f"{self.order.payment_status}"
    
    def __str__(self):
        return self.oid
    
    
class Certificate(models.Model):
    course=models.ForeignKey(Course,on_delete=models.CASCADE)
    user=models.ForeignKey(User,on_delete=models.CASCADE)
    certificate_id=ShortUUIDField(unique=True,length=6,max_length=20,alphabet='1234567890')
    date=models.DateTimeField(default=timezone.now) 
    
    def __str__(self):
        return self.course.title

class CompletedLessons(models.Model):
    course=models.ForeignKey(Course,on_delete=models.CASCADE)
    user=models.ForeignKey(User,on_delete=models.CASCADE,null=True,blank=True)
    variant_item=models.ForeignKey(VariantItem,on_delete=models.CASCADE)
    date=models.DateTimeField(default=timezone.now) 
    
    def __str__(self):
        return self.course.title
    
class EnrolledCourse(models.Model):
    
    course=models.ForeignKey(Course,on_delete=models.CASCADE)
    user=models.ForeignKey(User,on_delete=models.CASCADE)
    teacher=models.ForeignKey(Teacher,on_delete=models.CASCADE,null=True,blank=True)
    order_item=models.ForeignKey(CartOrderItem,on_delete=models.CASCADE)
    date=models.DateTimeField(default=timezone.now) 
    enrollement_id=ShortUUIDField(unique=True,length=6,max_length=20,alphabet='1234567890')
    date=models.DateTimeField(default=timezone.now) 
    
    def __str__(self):
        return self.course.title
    
    def lectures(self):
        return VariantItem.objects.filter(variant__course=self.course)
    
    def completed_lessons(self):
        return CompletedLessons.objects.filter(course=self.course,user=self.user)
    
    def curriculum(self):
        return Variant.objects.filter(course=self.course)
    
    def notes(self):
        return Note.objects.filter(user=self.user,course=self.course)
    
    def question_answer(self):
        return Question_Answer.objects.filter(course=self.course)
    
    def review(self):
        return Review.objects.filter(course=self.course,user=self.user).first()
    

class Note(models.Model):
    course=models.ForeignKey(Course,on_delete=models.CASCADE)
    user=models.ForeignKey(User,on_delete=models.CASCADE,null=True,blank=True)     
    title=models.CharField(max_length=1000,null=True,blank=True)
    note=models.TextField()
    note_id=ShortUUIDField(unique=True,length=6,max_length=20,alphabet='1234567890')
    date=models.DateTimeField(default=timezone.now)
    
    
    def __str__(self):
        return self.title
    
    
class Review(models.Model):
    course=models.ForeignKey(Course,on_delete=models.CASCADE)
    user=models.ForeignKey(User,on_delete=models.CASCADE,null=True,blank=True) 
    review=models.TextField()
    rating=models.IntegerField(choices=RATING,default=None) 
    reply=models.CharField(null=True,blank=True,max_length=1000)
    active=models.BooleanField(default=True)
    date=models.DateTimeField(default=timezone.now)
    
    def __str__(self):
        return self.course.title
    
    def profile(self):
        return Profile.objects.get(user=self.user)
    
class Notification(models.Model):
    user=models.ForeignKey(User,on_delete=models.CASCADE,null=True,blank=True) 
    teacher=models.ForeignKey(Teacher,on_delete=models.CASCADE,null=True,blank=True)
    order=models.ForeignKey(CartOrder,on_delete=models.SET_NULL,null=True,blank=True)
    order_item=models.ForeignKey(CartOrderItem,on_delete=models.SET_NULL,null=True,blank=True)
    review=models.ForeignKey(Review,on_delete=models.SET_NULL,null=True,blank=True)
    type_notification=models.CharField(max_length=100,choices=NOTI_TYPE)
    seen=models.BooleanField(default=False)
    date=models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.type_notification
    
class Coupon(models.Model):
    teacher=models.ForeignKey(Teacher,on_delete=models.CASCADE,null=True,blank=True)
    used_by=models.ManyToManyField(User,blank=True)
    code=models.CharField(max_length=50)
    discount=models.IntegerField(default=1)
    active=models.BooleanField(default=True)
    date=models.DateTimeField(default=timezone.now)
    
    def __str__(self):
        return self.code
    
class Wishlist(models.Model):
    course=models.ForeignKey(Course,on_delete=models.CASCADE)
    user=models.ForeignKey(User,on_delete=models.CASCADE,null=True,blank=True) 
    
    def __str__(self):
        return self.course
    
class Country(models.Model):
    name=models.CharField(max_length=100)
    tax_rate=models.IntegerField(default=5)
    active=models.BooleanField(default=True)
    
    def __str__(self):
        return self.name
    

    

    
    
    
    
    
            
            
    
    
        
    
    
    
          
    
    
    
    
    
    
        
    
    
    
    
     