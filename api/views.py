from django.contrib.auth.mixins import UserPassesTestMixin
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response
from courses.models import Subject, Course
from api.serializers import SubjectSerializer, CourseWithContentSerializer


class SubjectListView(generics.ListCreateAPIView):
    serializer_class = SubjectSerializer
    queryset = Subject.objects.all()


class SubjectDetailView(generics.RetrieveAPIView):
    serializer_class = SubjectSerializer
    queryset = Subject.objects.all()


class CourseListView(APIView, UserPassesTestMixin):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        courses = Course.objects.all().filter(subject__id=pk)
        serializer = CourseWithContentSerializer(courses, many=True)
        return Response(serializer.data)
