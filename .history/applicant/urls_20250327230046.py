from django.urls import path
from .views import applicant_dashboard
from . import views

urlpatterns = [
    path('dashboard/', applicant_dashboard, name='applicant_dashboard'),
    path('job-list/', views.applicant_job_list, name='applicant_job_list'),

]
