from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.contrib import messages
from recruiter.forms import JobPostForm
from recruiter.models import JobPost
from people.models import CustomUser  # Import the user model
from django.http import HttpResponseForbidden
from django.contrib.staticfiles.storage import staticfiles_storage

def is_recruiter(user):
    """Helper function to check if the user is a recruiter."""
    return user.is_authenticated and user.role == "recruiter"

def get_recruiter_context(user):
    """Helper function to get recruiter-related context data."""
    profile_picture = user.profile_pic.url if user.profile_pic else staticfiles_storage.url('images/default-profile.png')
    return {
        "recruiter_name": user.username,
        "profile_picture": profile_picture,
    }

# 🔹 Recruiter Dashboard (Shows Only Recruiter's Jobs)
@login_required
def recruiter_dashboard(request):
    if request.user.role != 'recruiter':  # Ensure only recruiters access this view
        messages.error(request, "Unauthorized access.")
        return redirect('job_list')  # Redirect unauthorized users

    recruiter = request.user
    total_jobs = JobPost.objects.filter(recruiter=recruiter).count()

    # Calculate total applicants for all jobs posted by the recruiter
    total_applicants = Application.objects.filter(job_post__recruiter=recruiter).count()

    # Fetch only the recruiter's jobs
    recent_jobs = JobPost.objects.filter(recruiter=recruiter).order_by('-posted_at')[:4]

    # Get job status counts for this recruiter
    open_jobs = JobPost.objects.filter(recruiter=recruiter, status="open").count()
    closed_jobs = JobPost.objects.filter(recruiter=recruiter, status="closed").count()
    paused_jobs = JobPost.objects.filter(recruiter=recruiter, status="paused").count()

    # Get the number of applications for each job
    for job in recent_jobs:
        job.applicant_count = Application.objects.filter(job_post=job).count()

    context = {
        "total_jobs": total_jobs,
        "total_applicants": total_applicants,  # Updated to reflect actual count
        "recent_jobs": recent_jobs,
        "open_jobs": open_jobs,
        "closed_jobs": closed_jobs,
        "paused_jobs": paused_jobs,
    }
    context.update(get_recruiter_context(recruiter))
    return render(request, "recruiter/recruiter_dashboard.html", context)


# 🔹 Job List (Applicants See All, Recruiters See Their Jobs)
@login_required
def job_list(request):
    if request.user.role == 'recruiter':
        job_posts = JobPost.objects.filter(recruiter=request.user).order_by('-posted_at')
    else:
        job_posts = JobPost.objects.all().order_by('-posted_at')

    print(f"Jobs found: {job_posts.count()}")  # Debugging: Check if jobs exist

    paginator = Paginator(job_posts, 8)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'page_obj': page_obj,
    }
    context.update(get_recruiter_context(request.user))
    return render(request, 'recruiter/job_list.html', context)

# 🔹 Job Creation (Only Recruiters)
@login_required
def job_create_combined(request):
    if not is_recruiter(request.user):
        return HttpResponseForbidden("Only recruiters can post jobs.")

    if request.method == 'POST':
        form = JobPostForm(request.POST)
        if form.is_valid():
            job_post = form.save(commit=False)
            job_post.recruiter = request.user  # Assign recruiter
            job_post.status = 'open'
            job_post.save()
            return redirect('job_list')
    else:
        form = JobPostForm()

    context = {'form': form}
    context.update(get_recruiter_context(request.user))
    return render(request, 'recruiter/job_form_combined.html', context)


# 🔹 Job Edit (Only Recruiter Who Created It)
@login_required
def job_edit(request, id):
    job = get_object_or_404(JobPost, id=id)

    # 🚨 Ensure the logged-in recruiter is the job's owner
    if job.recruiter != request.user:
        messages.error(request, "You are not authorized to edit this job.")
        return redirect('recruiter_dashboard')  # Redirect unauthorized users

    if request.method == 'POST':
        form = JobPostForm(request.POST, instance=job)
        if form.is_valid():
            form.save()
            messages.success(request, "Job updated successfully!")
            return redirect('job_description', job_id=job.id)
        else:
            print(form.errors)  # Debugging errors
    else:
        form = JobPostForm(instance=job)

    context = {'form': form, 'job': job}
    context.update(get_recruiter_context(request.user))
    return render(request, 'recruiter/job_edit.html', context)


# 🔹 Job Delete (Only Recruiter Who Created It)
@login_required
def job_delete(request, id):
    job = get_object_or_404(JobPost, id=id)

    # 🚨 Ensure the logged-in recruiter is the job's owner
    if job.recruiter != request.user:
        messages.error(request, "You are not authorized to delete this job.")
        return redirect('recruiter_dashboard')  # Redirect unauthorized users

    job.delete()
    messages.success(request, "Job deleted successfully.")
    return redirect('job_list')


# View to show details of a single job post
def job_description(request, job_id):  # ✅ Match with URL pattern
    job = get_object_or_404(JobPost, id=job_id)
    context = {'job': job}
    context.update(get_recruiter_context(request.user))
    return render(request, 'recruiter/job_description.html', context)





from .models import Application

@login_required
def applications_list(request):
    # Fetch all applications for the jobs that the recruiter has posted
    job_posts = JobPost.objects.filter(recruiter=request.user)  # Assuming the recruiter is the logged-in user
    applications = Application.objects.filter(job_post__in=job_posts).order_by('-applied_at')

    # Pagination
    paginator = Paginator(applications, 10)  # Show 10 applications per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # Prepare the context with applicant details
    context = {
        "page_obj": page_obj,  # Pass the paginated applications to the template
    }

    return render(request, 'recruiter/applications_list.html', context)





#chatbots view
import os
import json
import requests
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from dotenv import load_dotenv

load_dotenv()  # Load environment variables

GOOGLE_GEMINI_API_KEY = os.getenv("GOOGLE_GEMINI_API_KEY")

@csrf_exempt
def chatbot(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            user_message = data.get("message", "").strip()

            if not user_message:
                return JsonResponse({"error": "Empty message"}, status=400)

            # Make a request to the Gemini API
            api_url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateText"
            headers = {"Content-Type": "application/json"}
            payload = {
                "prompt": {"text": user_message},
                "temperature": 0.7
            }
            response = requests.post(
                f"{api_url}?key={GOOGLE_GEMINI_API_KEY}",
                headers=headers,
                json=payload
            )

            if response.status_code != 200:
                return JsonResponse({"error": "Failed to fetch AI response"}, status=500)

            response_data = response.json()
            bot_response = response_data.get("candidates", [{}])[0].get("output", "Sorry, I didn't understand that.")

            return JsonResponse({"response": bot_response})

        except json.JSONDecodeError:
            return JsonResponse({"error": "Invalid JSON"}, status=400)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)

    return JsonResponse({"error": "Invalid request"}, status=400)
