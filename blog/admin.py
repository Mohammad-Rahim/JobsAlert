from django.contrib import admin
from blog.models import Post, JobApplication, Category

@admin.register(Post)
class PostAdmin(admin.ModelAdmin):

    list_display = (
        'title',
        'date_posted',
        'author',
        'category',
    )


@admin.register(JobApplication)
class JobApplicationAdmin(admin.ModelAdmin):

    list_display = (
        'sno',
        'user',
        'post',
    )

admin.site.register(Category)