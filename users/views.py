from django.shortcuts import render, redirect 
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .forms import UserRegisterForm, UserUpdateForm, ProfileUpdateForm, UserProfileForm
from icecream import ic
# Create your views here.

def register(request):
    register_personnel=request.GET.get('register_personnel')
    register_organization=request.GET.get('register_organization')
    ic(
        register_personnel,
        register_organization
    )
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        profile_form = UserProfileForm(request.POST)
        if form.is_valid():
            user = form.save()
        
            profile_form = UserProfileForm(request.POST, instance=user.profile)
            if profile_form.is_valid():
                profile_form.save()
                messages.success(request, f'Your account has been created successfully! You can now log in.')
                return redirect('login')

            else:
                form = UserRegisterForm()
                profile_form = UserProfileForm(request.POST)
                # user = form.save()

            # profile = profile_form.save(commit=False)
            # profile.user = user
            # profile.save()
            # username = form.cleaned_data.get('username')
            # messages.success(request, f'Your account has been created successfully! You can now log in.')
            # return redirect('login')
    else:
        value = 'personal'
        form = UserRegisterForm()
        if register_personnel:
            value='personal'
        elif register_organization:
            value='organization'
        profile_form = UserProfileForm(initial={'account_type': value})
    context = {'form': form, 'profile_form': profile_form}
    return render(request, 'users/register.html', context)


@login_required
def profile(request):
    if request.method == 'POST':
        u_form = UserUpdateForm(request.POST, instance=request.user)
        p_form = ProfileUpdateForm(request.POST, request.FILES, instance=request.user.profile)

        if u_form.is_valid() and p_form.is_valid():
            u_form.save()
            p_form.save()
            messages.success(request, 'Your account has been updated successfully!')
            return redirect('profile')
    else:
        u_form = UserUpdateForm(instance=request.user)
        p_form = ProfileUpdateForm(instance=request.user.profile)

    context = {
        'u_form': u_form,
        'p_form': p_form
    }
    return render(request, 'users/profile.html', context)
