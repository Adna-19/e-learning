from .models import Order
from datetime import datetime
import json

def get_total_cart_items(request):
	if request.user.is_authenticated and request.user.user_role == 'S':
		student = request.user.student_profile
		try:
			order = Order.objects.get(customer=student, complete=False)
			total_items = order.get_cart_items
		except:
			total_items = 0
	else:
		try:
			cart = json.loads(request.COOKIES['cart'])
		except: 	cart = {}
		total_items = len(cart)
		
	return {'total_items':total_items}

def get_trashed_courses(request):
	try:
		if request.user.instructor_profile:
			trashed_courses = request.user.instructor_profile.courses.filter(trashed=True)
			context = {'trashed_courses': trashed_courses, 'trashed_courses_count': trashed_courses.count()}
	except:
		context = {}
	return context