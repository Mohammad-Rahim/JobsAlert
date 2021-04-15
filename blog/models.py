from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
from django.urls import reverse
from phone_field import PhoneField
from django import forms 

# Create your models here.

class Category(models.Model):

    category_name = models.CharField(max_length = 50, verbose_name='Category Name')
    image = models.ImageField(upload_to='category_images/', null=True, blank=True)

    def __str__(self):
        return self.category_name

class Post(models.Model):
    # sno = models.AutoField(primary_key=True, default=None)
    title = models.CharField(max_length=100)
    content = models.TextField()
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        related_name='posts',
        related_query_name='posts',
        null=True,
    )
    date_posted = models.DateTimeField(default=timezone.now)
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    due_date = models.DateTimeField()

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse("post-detail", kwargs={"pk": self.pk})    

    def get_application_count(self):
        return self.job_applications.count()  


class JobApplication(models.Model):
    sno = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        related_name='job_applications',
        related_query_name='job_applications'
    )
    name = models.CharField(max_length=200)
    email = models.EmailField(max_length=100)
    phone = PhoneField(blank=True, help_text='Enter phone number')
    work_experience = models.TextField()
    resume = models.FileField(upload_to = 'resume', default='resume/default_resume.jpg')
    status = models.CharField(max_length=200, default='pending')

    def __str__(self):
        return self.name
    