from django.urls import path
from django.views.decorators.cache import cache_page

from . import views

app_name = 'students'
urlpatterns = [

    path('register/', views.StudentRegistrationView.as_view(), name='student_registration'),
    path('enroll-course/', views.StudentEnrollCourseView.as_view(), name='student_enroll_course'),
    path('courses/', views.StudentCourseListView.as_view(), name='student_course_list'),
    path('course/<course_id>/', cache_page(60 * 15)(views.StudentCourseModuleView.as_view()),
         name='student_course_detail'),
    path('course/<course_id>/module/<module_id>/content/',
         cache_page(60 * 15)(views.StudentModuleContentView.as_view()), name='student_module_content'),
]
