from django.utils import timezone
from .models import Post

def get_latest_jobs(request):
    posts = Post.objects.filter(due_date__gte=timezone.now()).order_by('due_date')[:4]
    return {
        'hot_box_posts': posts
    }