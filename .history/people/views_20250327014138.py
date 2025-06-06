from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from .forms import CustomUserCreationForm, CustomLoginForm
from django.contrib.auth.decorators import login_required
import shutil
from django.conf import settings
import os

def register(request):
    """ Register a new user with profile picture handling """
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST, request.FILES)
        if form.is_valid():
            user = form.save(commit=False)
            
            # Handle user role fields
            if user.role == 'recruiter':
                user.resume = None  # Recruiters don't need resumes
            elif user.role == 'applicant':
                user.company_name = None  # Applicants don't need company names
            
            # Handle profile picture
            from django.conf import settings
            import os
            from django.core.files import File

            if 'profile_pic' in request.FILES:
                user.profile_pic = request.FILES['profile_pic']
            else:
                default_image_path = os.path.join(settings.BASE_DIR, 'static', 'images', 'profile.png')

                if os.path.exists(default_image_path):
                    with open(default_image_path, 'rb') as f:
                        user.profile_pic.save('profile.png', File(f))
                else:
                    print("Default profile image not found!")

            user.save()
            login(request, user)
            return redirect('dashboard_redirect')
    else:
        form = CustomUserCreationForm()
    
    return render(request, 'people/register.html', {'form': form})




def user_login(request):
    """ Login View """
    if request.method == 'POST':
        form = CustomLoginForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('dashboard_redirect')
    else:
        form = CustomLoginForm()

    return render(request, 'people/login.html', {'form': form})

@login_required
def user_logout(request):
    """ Logout View """
    logout(request)
    return redirect('user_login')

@login_required
def dashboard_redirect(request):
    """ Redirect user based on role """
    if request.user.role == 'recruiter':
        return redirect('recruiter_dashboard')
    else:
        return redirect('applicant_dashboard')
