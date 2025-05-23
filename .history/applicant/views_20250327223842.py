from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.utils.timezone import now
from datetime import timedelta
from recruiter.models import Application

@login_required
def applicant_dashboard(request):
    user = request.user

    # Ensure only applicants access this page
    if user.role != "applicant":
        return render(request, "error.html", {"message": "Access Denied"})

    applications = Application.objects.filter(applicant_email=user.email).order_by("-applied_at")
    total_applications = applications.count()

    # Job Application Trend (Last 6 Months)
    last_six_months = [now().replace(day=1) - timedelta(days=30 * i) for i in reversed(range(6))]
    months = [date.strftime("%b") for date in last_six_months]

    application_counts = [
        applications.filter(applied_at__year=date.year, applied_at__month=date.month).count()
        for date in last_six_months
    ]

    context = {
        "applicant_name": user.first_name or user.username,
        "profile_picture": user.profile_pic.url if user.profile_pic else "/static/images/default-profile.png",
        "total_applications": total_applications,
        "recent_applications": applications[:5],  # Fetch only 5 recent applications
        "months": months,
        "application_counts": application_counts,
    }

    return render(request, "applicant/applicant_dashboard.html", context)
