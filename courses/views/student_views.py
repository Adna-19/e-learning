from django.views.generic.list import ListView
from django.urls import reverse
from django.shortcuts import get_object_or_404, redirect
from django.views.generic.detail import DetailView
from django.views.generic.base import View, TemplateResponseMixin
from django.views.generic import FormView, TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.contenttypes.models import ContentType
from django.forms.models import model_to_dict
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from braces.views import CsrfExemptMixin, JsonRequestResponseMixin
from accounts.models import StudentProfile, InstructorProfile
from ..models import Course, Module, Subject, Review, Notification, Acheivement
from courses.models import Order, OrderItem
from datetime import datetime
from django.core.cache import cache
from django.core import serializers
from django.core.files import File
from ..utils import (
	cookie_cart, 
	mark_module_as_completed, 
	mark_content_as_completed, 
	render_to_pdf
)
from django.db.models import Count
from django.utils import timezone
from django.utils.dateformat import format
from paypal.standard.forms import PayPalPaymentsForm
import json
from io import BytesIO

class ClassroomDashboardView(TemplateResponseMixin, View):
	template_name = 'courses/site/classroom.html'

	def get(self, request, *args, **kwargs):
		student = request.user.student_profile

		latest_activity   = Course.objects.latest_activity(student)
		completed_courses = Course.objects.completed_courses(student)[:2]
		free_courses      = Course.objects.enrolled_courses(student, payment_status='free')
		paid_courses      = Course.objects.enrolled_courses(student, payment_status='paid')

		return self.render_to_response({
			'student': student,
			'latest_activity': latest_activity,
			'free_courses': free_courses,
			'paid_courses': paid_courses,
			'completed_courses': completed_courses
		})

class ClassroomCourseDetailView(TemplateResponseMixin, View):
	template_name = 'courses/site/classroom_course_details.html'

	def get(self, request, *args, **kwargs):
		course = get_object_or_404(Course, slug=kwargs['course_slug'])

		return self.render_to_response({
			'course': course,
			'modules': course.modules.all()
		})

class ClassroomModuleContentsView(TemplateResponseMixin, View):
	template_name = 'courses/site/classroom_modules_contents.html'

	def get(self, request, *args, **kwargs):
		quiz = None
		student = request.user.student_profile
		completed_courses = Course.objects.completed_courses(student)

		course = get_object_or_404(Course, slug=kwargs['course_slug'])
		module = course.modules.get(slug=kwargs['module_slug']) # 2 -> 3

		content = module.contents.get(order=kwargs['next_content']) if 'next_content' in kwargs else module.contents.first()
		mark_content_as_completed(student, content)

		content_template_name = f'courses/site/contents/{content.content_type.model}_content.html'

		next_content_order = content.order + 1
		next_module_order = module.order + 1

		try:
			next_module = course.modules.get(order=next_module_order) if next_content_order == module.contents.count() else None
			mark_module_as_completed(request.user.student_profile, module)
		
		except Module.DoesNotExist:
			if module == course.modules.last() and course not in completed_courses:
				mark_module_as_completed(request.user.student_profile, module)  # mark the last module as viewed
			next_module = None

		if next_module:
			try:
				quiz = module.attached_quiz
			except:	pass

		return self.render_to_response({
			'course': course,
			'current_module': module,
			'next_module': next_module,
			'quiz': quiz,
			'content': content,
			'next_content': next_content_order, 
			'content_template': content_template_name
		})

class ClassroomAcheivementsView(TemplateResponseMixin, View):
	template_name = 'courses/site/classroom_acheivements.html'

	def get(self, request, *args, **kwargs):
		student = request.user.student_profile
		return self.render_to_response({
			'achievements': student.achievements.all().order_by('-date_created'),
		})

class completeCourseAndGenerateCertificate(TemplateResponseMixin, View):
	template_name = 'courses/site/certification.html'

	def get(self, request, course_slug, *args, **kwargs):
		student = request.user.student_profile
		course = Course.objects.enrolled_courses(student).get(slug=course_slug)
		
		if course not in Course.objects.completed_courses(student):
			acheivement = Acheivement(student=student, course=course)
			acheivement.save()
		else:
			acheivement = None

		certificate_template = 'courses/site/certificate.html'
		context = {'course': course, 'student': student, 'today': timezone.now()}

		pdf = render_to_pdf(certificate_template, context)

		if pdf:
			response = HttpResponse(pdf, content_type='application/pdf')
			filename = f'{student.user.username}_{timezone.now()}.pdf'
			content = f"inline; filename={filename}"
			download = request.GET.get('download')
			if download:
				if acheivement:
					acheivement.certificate.save(
						f'certificates/{student.user.username}/{filename}', 
						File(BytesIO(pdf.content))
					)
					acheivement.save()
				content = f"attachment; filename={filename}"
			response['Content-Disposition'] = content
			return response
		return HttpResponse("Not found")

class ProfileSettingView(TemplateResponseMixin, View):
	template_name = 'courses/site/profile_settings.html'

	def get(self, request, *args, **kwargs):
		student = request.user.student_profile
		enrolled_courses = Course.objects.enrolled_courses(student)
		completed_courses = Course.objects.completed_courses(student)

		return self.render_to_response({
			'student': student,
			'enrolled_courses': enrolled_courses,
			'completed_courses': completed_courses
		})

class HomePageView(TemplateResponseMixin, View):
	template_name = 'courses/site/home.html'

	def get(self, request, *args, **kwargs):
		featured_courses = Course.objects.order_by('-date_created')[:5]
		top_four_instructors = InstructorProfile.objects.all()[:4]

		return self.render_to_response({
			'featured_courses': featured_courses,
			'top_four_instructors': top_four_instructors
		})

class AboutPageView(TemplateResponseMixin, View):
	template_name = 'courses/site/about.html'

	def get(self, request, *args, **kwargs):
		teachers = InstructorProfile.objects.all()

		return self.render_to_response({
			'teachers': teachers,
			'enrolled_students': 87211,
			'uploaded_courses': 91912,
			'people_certified': 65872,
			'global_teachers': 87121
		})

class ContactPageView(TemplateResponseMixin, View):
	template_name = 'courses/site/contact.html'

	def get(self, request, *args, **kwargs):
		return self.render_to_response({})

class StudentCoursesListView(ListView):
	model = Course
	paginate_by = 12
	template_name = 'courses/site/courses_list.html'
	context_object_name = 'courses'
	subject = None
	is_paid = None

	def get_subjects_from_db_or_cache(self):
		subjects = cache.get('subjects')
		if not subjects:
			subjects = Subject.objects.annotate(total_courses=Count('courses'))
			cache.set('subjects', subjects)
		return subjects

	def get_courses_from_db_or_cache(self):
		courses = cache.get('paid_courses') if self.is_paid else cache.get('free_courses')
		if not courses:
			courses = Course.objects.paid_courses() if self.is_paid else Course.objects.free_courses()
			cache.set('paid_courses', courses) if self.is_paid else cache.set('free_courses', courses)
		return courses

	def get_courses_by_subject_from_cache_or_db(self, subject):
		key = f'subject_{subject.name}_courses'
		courses = cache.get(key)
		if not courses:
			courses = self.get_queryset().annotate(total_modules=Count('modules'))
			cache.set(key, courses)
		return courses		

	def dispatch(self, request, slug=None, paid=None, *args, **kwargs):
		if slug:	self.subject = get_object_or_404(Subject, slug=slug)
		self.is_paid = True if paid == 1 else False
		return super(StudentCoursesListView, self).dispatch(request, slug, *args, **kwargs)

	def get_queryset(self):
		qs = super().get_queryset().filter(trashed=False)
		if self.subject:
			return qs.filter(subject=self.subject)
		return qs
	
	def get_context_data(self, **kwargs):
		context = super().get_context_data(**kwargs)
		subjects = self.get_subjects_from_db_or_cache()

		if self.subject:
			courses = self.get_courses_by_subject_from_cache_or_db(self.subject)
		else:
			courses = self.get_courses_from_db_or_cache()

		context['subjects'] = subjects
		context['courses'] = courses
		context['is_paid'] = self.is_paid
		return context

class StudentCourseDetailView(DetailView):
	model = Course
	context_object_name = 'course'
	template_name = 'courses/site/course_detail.html'

class StudentCourseModuleDetailView(DetailView):
	model = Module
	context_object_name = 'module'
	template_name = 'courses/site/module_detail.html'

class StudentCourseEnrollmentView(LoginRequiredMixin, View):

	def get(self, request, slug, id, *args, **kwargs):
		student = get_object_or_404(StudentProfile, id=id)
		course = get_object_or_404(Course, slug=slug)
		if course.payment_status == 'free':
			# add student to enrolled students
			course.students.add(student)
		else:
			# navigate to payment method
			return HttpResponse(f'<h1>First you have to pay {course.price} for course</h1>')
		return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

class StudentCourseDisenrollmentView(LoginRequiredMixin, View):

	def get(self, request, slug, id,  *args, **kwargs):
		student = get_object_or_404(StudentProfile, id=id)
		course = get_object_or_404(Course, slug=slug)

		if course.payment_status == 'free':
			if request.user.student_profile in course.students.all():
				course.students.remove(student)
		else:
			return HttpResponse('<h1>Confirmation form here...</h1>')
		return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

class ShowCartItemsView(TemplateResponseMixin, View):
	template_name = 'courses/site/cart.html'

	def get(self, request, *args, **kwargs):
		
		if request.user.is_authenticated:
			student = request.user.student_profile
			order = Order.objects.get(customer=student, complete=False)
			items = order.orderitem_set.all()
		else:
			cartData = cookie_cart(request)
			items = cartData['items']
			order = cartData['order']

		return self.render_to_response({
			'cart_items': items,
			'order': order
			})

class AddCourseToCartView(LoginRequiredMixin, View):

	def get(self, request, slug, *args, **kwargs):
		student = request.user.student_profile
		course = get_object_or_404(Course, slug=slug)
		order, created = Order.objects.get_or_create(
			customer=student, complete=False,
			defaults={ 'customer':student }
		)
		OrderItem.objects.create(course=course, order=order)
		return JsonResponse({'message': 'Item added successfully'})

class RemoveItemFromCartView(LoginRequiredMixin, View):
	
	def get(self, request, slug, *args, **kwargs):
		student = request.user.student_profile
		course = get_object_or_404(Course, slug=slug)
		order = Order.objects.get(customer=student, complete=False)
		item = order.orderitem_set.get(course=course)
		item.delete()
		return JsonResponse({'message': 'Item deleted successfully' })

class PayPalPaymentView(FormView):
	template_name = 'courses/site/paypal_form.html'
	amount = None
	form_class = PayPalPaymentsForm

	def dispatch(self, request, amount, *args, **kwargs):
		self.amount = amount
		return super(PayPalPaymentView, self).dispatch(request, amount, *args, **kwargs)

	def get_initial(self):
		return {
      "business": 'edubin@gmail.com',
      "amount": self.amount,
      "currency_code": "USD",
      "item_name": 'My First Course Set',
      "invoice": f"{str(datetime.now().timestamp())}",
      "notify_url": self.request.build_absolute_uri(reverse('paypal-ipn')),
      "return_url": self.request.build_absolute_uri(reverse('paypal-return')),
      "cancel_return": self.request.build_absolute_uri(reverse('paypal-cancel')),
      "lc": 'EN',
      "no_shipping": '1',
    }

class PayPalPaymentSuccessView(TemplateResponseMixin, View):
	template_name = 'courses/site/paypal_success.html'

	def get(self, request, *args, **kwargs):
		student = request.user.student_profile
		order = get_object_or_404(Order, customer=student, complete=False)

		for orderitem in order.orderitem_set.all():
			orderitem.course.students.add(student)

		order.transaction_id = str(datetime.now().timestamp())
		order.complete = True 
		order.save()
		return self.render_to_response({})

class PayPalPaymentRejectView(TemplateView):
	template_name = 'courses/site/paypal_cancel.html'

class TeachersListView(ListView):
	model = InstructorProfile
	paginate_by = 8
	template_name = 'courses/site/teachers/list.html'
	context_object_name = 'teachers'

class TeacherDetailView(DetailView):
	model = InstructorProfile
	template_name = 'courses/site/teachers/detail.html'
	context_object_name = 'teacher'

class StudentCourseReviewAndRatingView(CsrfExemptMixin, JsonRequestResponseMixin, LoginRequiredMixin, View):
	def post(self, request, course_slug, *args, **kwargs):
		course = get_object_or_404(Course, slug=course_slug)
		rating = request.POST['rating']
		comment = request.POST['comment']

		new_review = Review(course=course, user=request.user, rating=rating, comment=comment)
		new_review.save()

		Notification.objects.create(
			receiver=course.instructor.user,
			sender=request.user,
			content_type=ContentType.objects.get(app_label='courses', model='review'),
			object_id=new_review.id,
			status='review'
		)

		review_data = {
			'profile_image': request.user.profile_image.url, 
			'username': request.user.full_name,
			'comment': new_review.comment,
			'rating': new_review.rating,
			'date_created': format(new_review.date_created, 'M, d Y')
		}

		return self.render_json_response(review_data)