from django.shortcuts import get_object_or_404
from django.conf import settings
import requests
from django.http import HttpResponse
from django.template.loader import get_template
from xhtml2pdf import pisa
from .models import *
import json
from io import BytesIO

def cookie_cart(request):
	items = []
	order = {'get_total_cart_price': 0, 'get_cart_items': 0}

	try:
		cart = json.loads(request.COOKIES['cart'])
	except: 	cart = {}

	for course_slug in cart:
		try:
			course = get_object_or_404(Course, slug=course_slug)
			order['get_total_cart_price'] += course.price
			order['get_cart_items'] += 1

			item = {
				'course': {
					'title': course.title,
					'subject': course.subject.name,
					'slug': course.slug,
					'instructor': course.instructor,
					'image': course.image,
					'description': course.description,
					'price': course.price,
					'date_created': course.date_created
				}
			}
			items.append(item)

		except Course.DoesNotExist:
			print('Course does not exists')

	return {'items': items, 'order': order}

def time_greeting_message(hour):
	message = ""
	if hour < 12:		
		message = "Good Morning"
	elif hour >= 12 and hour <= 17:
		message = "Good Afternoon"
	elif hour > 17 and hour <= 20:
		message = "Good Evening"
	else:
		message = "Good Night"
	return message

def get_weather_updates(city):
	url = 'http://api.openweathermap.org/data/2.5/weather?q={}&units=imperial&appid={}'
	city_weather = requests.get(url.format(city, settings.OPEN_WEATHER_API_KEY)).json()

	response_data = {
		'city' : city,
    'temperature' : city_weather['main']['temp'],
    'description' : city_weather['weather'][0]['description'],
    'icon' : city_weather['weather'][0]['icon']
	}
	return response_data

def mark_module_as_completed(student, module):
	not_viewed = student not in module.students_viewed.all()
	contents_not_remaining = all([student in content.students_viewed.all() for content in module.contents.all()])
	
	if not_viewed and contents_not_remaining:
		print(f'{module.order}: MODULE MARKED COMPLETED')
		module.students_viewed.add(student)

def mark_content_as_completed(student, content):
	if student not in content.students_viewed.all():
		content.students_viewed.add(student)

def render_to_pdf(template_src_path, context_data={}):
	template = get_template(template_src_path)
	html = template.render(context_data)
	result = BytesIO()
	try:
		pdf = pisa.pisaDocument(BytesIO(html.encode("utf-8")), result)
	except:
		pdf = None

	if not pdf.err:
		return HttpResponse(result.getvalue(), content_type='application/pdf')
	return None 