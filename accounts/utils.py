from django.shortcuts import get_object_or_404
from courses.models import Course, Order, OrderItem
import json

def not_enrolled(student, course):
	if student not in course.students.all():
		return True
	return False

def save_courses_from_cookies_to_order(request, student):
	order, created = Order.objects.get_or_create(
		customer=student, complete=False,
		defaults={'customer': student}
	)
	cart = json.loads(request.COOKIES['cart'])

	if cart:
		for course_slug in cart:
			course = get_object_or_404(Course, slug=course_slug)
			course_already_in_cart = OrderItem.objects.filter(order=order, course=course).exists()
			if not course_already_in_cart and not_enrolled(student, course):
				OrderItem.objects.create(order=order, course=course)