from django.shortcuts import render, redirect
from .models import JobPost
#from .forms import JobPostForm  # We'll create this form next
from django.core.paginator import Paginator
from django.shortcuts import render, get_object_or_404
from .forms import JobPostForm
from django.contrib import messages
from django.contrib.auth.decorators import login_required



# View to list all job posts
def job_list(request):
    job_posts = JobPost.objects.all()
    return render(request, 'recruiter/job_list.html', {'job_posts': job_posts})

# View to show details of a single job post
def job_detail(request, pk):
    job_post = JobPost.objects.get(pk=pk)
    return render(request, 'recruiter/job_detail.html', {'job_post': job_post})


#testing




@login_required
def job_create_combined(request):
    if request.method == 'POST':
        form = JobPostForm(request.POST)
        if form.is_valid():
            job_post = form.save(commit=False)
            job_post.recruiter = request.user  # Assign the logged-in recruiter
            job_post.status = 'open'  # Default job status
            job_post.save()
            return redirect('job_list')  # Redirect to job listing page
    else:
        form = JobPostForm()

    return render(request, 'recruiter/job_form_combined.html', {'form': form})

def job_post_success(request):
    return 


def job_list(request):
    # Get all jobs, ordered by creation date (or you can change it to your preference)
    job_posts = JobPost.objects.all().order_by('-posted_at')

    # Paginate the job list (8 items per page)
    paginator = Paginator(job_posts, 8)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # If there are no jobs, display the 'No active jobs' message and hide pagination
    if not page_obj.has_other_pages():
        show_pagination = False
    else:
        show_pagination = True

    return render(request, 'recruiter/job_list.html', {
        'page_obj': page_obj,
        'show_pagination': show_pagination
    })


def job_description(request, job_id):
    job = get_object_or_404(JobPost, id=job_id)
    return render(request, 'recruiter/job_description.html', {'job': job})





def job_edit(request, id):
    job = get_object_or_404(JobPost, id=id)  # Fetch the job by ID

    if request.method == 'POST':
        form = JobPostForm(request.POST, instance=job)  # Pass existing job to form
        if form.is_valid():
            form.save()  # Save changes to the database
            return redirect('job_description', job_id=job.id)  # Redirect after saving
        else:
            print(form.errors)  # Debugging: Print form errors if validation fails
    else:
        form = JobPostForm(instance=job)  # Pre-populate form with existing data

    return render(request, 'recruiter/job_edit.html', {'form': form, 'job': job})



def job_delete(request, id):
    job = get_object_or_404(JobPost, id=id)
    job.delete()
    messages.success(request, "Job deleted successfully.")
    return redirect('job_list')  # Redirect to the job list page


def recruiter_dashboard(request):
    total_jobs = JobPost.objects.count()
    total_applicants = 232  # Placeholder (update if you have an Applicant model)

    # Get last 4 posted jobs
    recent_jobs = JobPost.objects.order_by('-posted_at')[:4]

    # Get job status counts
    open_jobs = JobPost.objects.filter(status="open").count()
    closed_jobs = JobPost.objects.filter(status="closed").count()
    paused_jobs = JobPost.objects.filter(status="paused").count()

    context = {
        "total_jobs": total_jobs,
        "total_applicants": total_applicants,
        "recent_jobs": recent_jobs,
        "open_jobs": open_jobs,
        "closed_jobs": closed_jobs,
        "paused_jobs": paused_jobs,
    }
    return render(request, "recruiter/recruiter_dashboard.html", context)