from django.shortcuts import render, get_object_or_404
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.models import User
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from .models import Post, JobApplication, Category
from django.contrib import messages
from django.core.paginator import Paginator
from django.core.files.storage import FileSystemStorage
from django.shortcuts import redirect
from django.urls import reverse
from django.core.mail import send_mail
from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.utils import timezone
from django.contrib.auth.decorators import login_required

class PostListView(ListView, LoginRequiredMixin):
    model = Post
    template_name = 'blog/home.html'
    context_object_name = 'posts'
    ordering = ['-date_posted']
    paginate_by = 5

    def get(self, request, *args, **kwargs):

        category_request = request.GET.get('category')
        if category_request:
            try:
                category = Category.objects.get(category_name__iexact=category_request)
                posts = category.posts.all()
            except Category.DoesNotExist:
                posts =  Post.objects.all()
        else:
            posts =  Post.objects.all()

        self.object_list = posts.filter(due_date__gte=timezone.now()).order_by('-date_posted')

        allow_empty = self.get_allow_empty()
        if not allow_empty:
            # When pagination is enabled and object_list is a queryset,
            # it's better to do a cheap query than to load the unpaginated
            # queryset in memory.
            if self.get_paginate_by(self.object_list) is not None and hasattr(self.object_list, 'exists'):
                is_empty = not self.object_list.exists()
            else:
                is_empty = not self.object_list
            if is_empty:
                raise Http404(_('Empty list and “%(class_name)s.allow_empty” is False.') % {
                    'class_name': self.__class__.__name__,
                })
        context = self.get_context_data()
        return self.render_to_response(context)

class UserPostListView(ListView):
    model = Post
    template_name = 'blog/user_posts.html'
    context_object_name = 'posts'
    paginate_by = 5

    def get_queryset(self):
        user = get_object_or_404(User,username=self.kwargs.get('username'))
        return Post.objects.filter(author=user).order_by('-date_posted')


class PostDetailView(DetailView, LoginRequiredMixin):
    model = Post
    

class PostCreateView(LoginRequiredMixin, CreateView):
    model = Post
    fields = ['title', 'content', 'due_date', 'category']

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)

class PostUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Post
    fields = ['title', 'content', 'due_date']

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)

    def test_func(self):
        post = self.get_object()
        if self.request.user == post.author:
            return True
        return False

class PostDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Post
    success_url = '/'

    def test_func(self):
        post = self.get_object()
        if self.request.user == post.author:
            return True
        return False
    

def about(request):
    return render(request, 'blog/about.html', {'title': 'About'})

@login_required(login_url='/login')
def job_apply(request, pk):
    context = {
        'profile_email' : request.user.email,
        'profile_username' : request.user.username
    }
    if request.method=="POST" and request.FILES['myfile']:

        myfile = request.FILES['myfile']
        # fs = FileSystemStorage()
        # filename = fs.save(myfile.name, myfile)
        # uploaded_file_url = fs.url(filename)

        name = request.POST.get("name")
        email = request.POST.get("email")
        phone = request.POST.get("phone")
        work_experience = request.POST.get("wexperience")
        user = request.user
        post = Post.objects.filter(pk=pk).first()

        apply_job = JobApplication(name=name, email=email, phone=phone, work_experience=work_experience, user=user, post=post, resume= myfile)
        apply_job.save()
        messages.success(request, "Your application has been posted successfully!!")

    return render(request, 'blog/job_apply.html', context)

def job_search(request):
    query = request.GET['query']
    
    if len(query)>70:
        allPosts = Post.objects.none()
    else:
        allPostsTitle = Post.objects.filter(title__icontains=query)
        allPostsContent = Post.objects.filter(content__icontains=query)
        allPosts = allPostsTitle.union(allPostsContent)

        paginator = Paginator(allPosts, 25) 

    if allPosts.count() == 0:
        messages.warning(request, "No search results found. Please search valid content.")    
    context = {'allPosts': allPosts}

    return render(request, 'blog/search.html', context)

def job_dashboard(request, pk):
    post = Post.objects.filter(pk=pk).first()
    job_applicants = JobApplication.objects.filter(post=post)
    
    total_applicants = job_applicants.count()

    pending_count = JobApplication.objects.filter(post=post, status='pending').count()
    approved_count = JobApplication.objects.filter(post=post, status='approved').count()
    # print(pending_count)

    context = { 'job_applicant': job_applicants,
                'total_applicants': total_applicants,
                'pending_count': pending_count,
                'approved_count': approved_count
                }
    return render(request, 'blog/dashboard.html', context)


def applicant_detail(request, pk, sno):
    post = Post.objects.filter(pk=pk).first()
    job_applicant = JobApplication.objects.filter(post=post)

    applicant_detail = JobApplication.objects.filter(sno=sno).first()
    # print(applicant_detail)
    # print(applicant_detail.name)
    # print(applicant_detail.email)

    context = {
        'applicant_detail': applicant_detail
    }

    return render(request, 'blog/applicant_detail.html', context)


def job_applicant_delete(request, pk, sno):

    if request.method == 'POST':
        post = Post.objects.filter(pk=pk).first()
        

        applicant = JobApplication.objects.filter(sno=sno).first()
        subject = 'Your job application has been declined.'

        from_email, to = settings.EMAIL_HOST_USER, JobApplication.objects.get(sno=sno).email
        html_content = render_to_string('blog/job_status.html', {'status':'declined', 'project_name': JobApplication.objects.get(sno=sno).post.title, 'user':JobApplication.objects.get(sno=sno).name})
        text_content = strip_tags(html_content)

        msg = EmailMultiAlternatives(subject, text_content, from_email, [to])
        msg.attach_alternative(html_content, "text/html")
        msg.send()

        applicant.delete()
        messages.success(request, "Applicant successfully deleted.")
        job_applicant = JobApplication.objects.filter(post=post)
        total_applicants = job_applicant.count()
        pending_count = JobApplication.objects.filter(post=post, status='pending').count()
        approved_count = JobApplication.objects.filter(post=post, status='approved').count()


        context = {'job_applicant': job_applicant,
                    'total_applicants': total_applicants,
                    'pending_count': pending_count,
                    'approved_count': approved_count
                }
        return render(request, 'blog/dashboard.html', context)

    else:
        return render(request, 'blog/application_confirm_delete.html')

    return render(request, 'blog/dashboard.html', context)


def job_applicant_approve(request, pk, sno):

    if request.method == 'POST':
        post = Post.objects.filter(pk=pk).first()
        
        applicant = JobApplication.objects.filter(sno=sno).update(status='approved')
        # applicant.update(status='approved')
        messages.success(request, "Applicant approved successfully.")
        subject = 'Your job application has been approved'

        from_email, to = settings.EMAIL_HOST_USER, JobApplication.objects.get(sno=sno).email
        html_content = render_to_string('blog/job_status.html', {'status':'approved', 'project_name': JobApplication.objects.get(sno=sno).post.title, 'user':JobApplication.objects.get(sno=sno).name})
        text_content = strip_tags(html_content)

        msg = EmailMultiAlternatives(subject, text_content, from_email, [to])
        msg.attach_alternative(html_content, "text/html")
        msg.send()

        job_applicant = JobApplication.objects.filter(post=post)
    
        total_applicants = job_applicant.count()
        pending_count = JobApplication.objects.filter(post=post, status='pending').count()
        approved_count = JobApplication.objects.filter(post=post, status='approved').count()



        context = {'job_applicant': job_applicant,
                    'total_applicants': total_applicants,
                    'pending_count': pending_count,
                    'approved_count': approved_count
                }
        return render(request, 'blog/dashboard.html', context)

    else:
        return render(request, 'blog/application_approve.html')

    return render(request, 'blog/dashboard.html', context)


