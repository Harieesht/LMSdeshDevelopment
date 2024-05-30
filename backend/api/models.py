from django.db import models
from userauths.models import User,Profile
from django.utils.text import slugify
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
    
    def course(self):
        return Course.objects.filter(Category=self).count()
    
    def save(self,*args,**kwargs):
        if self.slug == "" or self.slug == None:
            self.slug= slugify(self.title)
        
        super(Category,self).save(*args,**kwargs)
        
        
class Course(models.Model):
    category=models.ForeignKey(Category,on_delete=models.SET_NULL,null=True,blank=True)
    teacher=models.ForeignKey(Teacher,)
            
    
    
    
    
    
    
        
    
    
    
    
     