from rest_framework.permissions import BasePermission
from accounts.models import StudentProfile
from django.shortcuts import get_object_or_404

class IsEnrolled(BasePermission):
	def has_object_permission(self, request, view, obj):
		student = get_object_or_404(StudentProfile, user=request.user)
		return obj.students.filter(id=student.id).exists()