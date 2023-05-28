from django.urls import path
from .views import SubjectListView, SubjectDetailView, CourseListView

app_name = "api"

urlpatterns = [

    path('subjects/', SubjectListView.as_view(), name='subjects'),
    path('subjects/<pk>/', SubjectDetailView.as_view(), name='subject_detail'),
    path('subject/<pk>/courses/', CourseListView.as_view(), name='courses'),

]