from rest_framework import generics
from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.authentication import BasicAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework import viewsets
from rest_framework.decorators import action
from ..models import Subject, Course
from accounts.models import StudentProfile
from .serializers import (
	SubjectSerializer, 
	CourseSerializer, 
	CourseWithContentsSerializer
)
from .permissions import IsEnrolled

class SubjectListView(generics.ListAPIView):
	queryset = Subject.objects.all()
	serializer_class = SubjectSerializer

class SubjectDetailView(generics.RetrieveAPIView):
	queryset = Subject.objects.all()
	serializer_class = SubjectSerializer

class CourseViewSet(viewsets.ReadOnlyModelViewSet):
	queryset = Course.objects.all()
	serializer_class = CourseSerializer

	@action(detail=True, methods=['post'], 
								authentication_classes=[BasicAuthentication],
								permission_classes=[IsAuthenticated])
	def enroll(self, request, pk, format=None):
		course = self.get_object()
		student = get_object_or_404(StudentProfile, user=request.user)
		course.students.add(student)
		return Response({'enrolled': True})

	@action(detail=True, 
					methods=['get'],
					serializer_class=CourseWithContentsSerializer,
					authentication_classes=[BasicAuthentication],
					permission_classes=[IsAuthenticated, IsEnrolled])
	def contents(self, request, *args, **kwargs):
		return self.retrieve(request, *args, **kwargs)