from django.utils import timezone
from .models import Post
from django.db.models import Count

def get_latest_jobs(request):
    posts = Post.objects.filter(due_date__gte=timezone.now()).order_by('due_date')[:4]
    return {
        'hot_box_posts': posts
    }

def get_hot_jobs(request):
    posts = Post.objects.annotate(
                num_applicants=Count('job_applications')
            ).order_by('-num_applicants')[:4]
    return {
        'hot_box_posts_second': posts
    }