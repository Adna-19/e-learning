from django import template
from django.template.defaultfilters import stringfilter
import markdown
from courses.models import Order, Course
from datetime import datetime
import json

register = template.Library()

@register.filter()
@stringfilter
def markdown_content(content):
	return markdown.markdown(
		content, 
		extensions=[
			'markdown.extensions.fenced_code',
			'markdown.extensions.codehilite',
			'markdown.extensions.tables'
		]
	)

@register.filter()
def alread_enrolled(user, course):
	if user in course.students.all():
		return True
	return False

@register.filter()
def is_not_in_cart(course, request):
	if request.user.is_authenticated:
		student = request.user.student_profile
		order, created = Order.objects.get_or_create(customer=student, complete=False)
		if created:
			order.transaction_id = datetime.now().timestamp()
		ordered_courses = [item.course for item in order.orderitem_set.all()] 
	else:
		try:
			cart = json.loads(request.COOKIES['cart'])
		except: cart = {}

		course = course.slug
		ordered_courses = cart.keys()

	if course not in ordered_courses:
		return True
	return False

@register.filter()
def unread_notifications(user):
	return user.received_notifications.filter(seen=False).count()

@register.filter(name='times') 
def times(number):
    return range(1, number+1)

@register.filter()
def format_message(status):
	if status == 'review':
		message = 'given a review on your Course'
	elif status == 'comment':
		message = 'commented on your Blog Post'
	elif status == 'enrolling':
		message = 'enrolled in your Course'
	elif status == 'reply':
		message = 'replied to your comment'
	return message

@register.filter()
def already_view(module, student):
	if student in module.students_viewed.all():
		return True
	return False

@register.filter()
def not_completed_and_continued(course, student):
	course_not_completed = course not in Course.objects.completed_courses(student)
	some_modules_viewed = any([already_view(module, student) for module in course.modules.all()])
	
	if course_not_completed and some_modules_viewed:
		return True
	return False

@register.filter()
def continue_url(course, student):
	continued_module = None
	continued_content = None

	for module in course.modules.all():
		if student not in module.students_viewed.all():
			continued_module = module
			break

	if continued_module:
		continued_content = continued_module.contents.filter(students_viewed__in=[student]).last()


	if continued_module and continued_content:
		return f'/course/student/classroom/course/{course.slug}/module/{continued_module.slug}/contents/{continued_content.order}/'
	return f'/course/student/classroom/course/{course.slug}/module/{continued_module.slug}/contents/'

@register.filter()
def in_progess(course, student):
	if not all([student in module.students_viewed.all() for module in course.modules.all()]):
		return True
	return False

# @register.filter()
# def completed_by_student(course, student):
# 	return course.completed_by_student(student)

@register.filter()
def percent_completed(course, student):
	completed_modules = course.modules.filter(students_viewed__in=[student]).count()
	total_modules = course.modules.count()
	return round((completed_modules/total_modules) * 100)