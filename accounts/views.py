from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy
from django.core.files import File
from django.contrib.auth.forms import AuthenticationForm, PasswordChangeForm
from django.contrib.auth import login, authenticate, logout
from django.contrib.sites.shortcuts import get_current_site
from django.contrib import messages
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_text
from django.views.generic.edit import FormView
from django.views.generic.base import RedirectView, View, TemplateResponseMixin
from braces.views import CsrfExemptMixin, JsonRequestResponseMixin
from django_email_verification import send_email

from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail

from .forms import (
	SignUpForm, 
	StudentProfileSettingForm,
	IntructorProfileSettingForm,
)
from .tokens import account_activation_token
from django.template.loader import render_to_string
from .models import User, StudentProfile, InstructorProfile
from accounts.utils import save_courses_from_cookies_to_order
from courses.models import Course
import json

class LoginView(FormView):

	form_class    = AuthenticationForm
	template_name = 'accounts/authentications/login.html'
	next_url		  = None

	def dispatch(self, request, *args, **kwargs):
		if 'next_url' in kwargs:
			self.next_url = kwargs['next_url']
		return super(LoginView, self).dispatch(request, *args, **kwargs)

	def form_valid(self, form):
		cd = form.cleaned_data
		user = authenticate(username=cd['username'], password=cd['password'])
		if user:
			login(self.request, user)
			if user.user_role == 'S':
				save_courses_from_cookies_to_order(self.request, user.student_profile)
		return super(LoginView, self).form_valid(form)

	def get_success_url(self):
		if self.next_url:
			return reverse_lazy(self.next_url)
		elif self.request.user.user_role == 'S':
			return reverse_lazy('home')
		elif self.request.user.user_role == 'I':
			return reverse_lazy('cms_home_page')
		return super(LoginView, self).get_success_url()

	def get_context_data(self, **kwargs):
		context = super().get_context_data(**kwargs)
		context['next_url'] = self.next_url
		return context

def logout_view(request):
	logout(request)
	response = redirect('login')
	response.delete_cookie('cart')
	return response

class SignUpView(TemplateResponseMixin, View):
	template_name = 'accounts/authentications/signup_form.html'
	model = None
	next_url = None

	def dispatch(self, request, user_role, *args, **kwargs):
		if user_role == 'S':
			self.model = StudentProfile
		elif user_role == 'I':
			self.model = InstructorProfile

		if 'next_url' in kwargs:
			self.next_url = kwargs['next_url']

		return super(SignUpView, self).dispatch(request, user_role, *args, **kwargs)

	def get(self, request, user_role, *args, **kwargs):
		form = SignUpForm()
		return self.render_to_response({'form':form, 'user_role': user_role})

	def post(self, request, user_role, *args, **kwargs):
		form = SignUpForm(request.POST)

		if form.is_valid():

			site = get_current_site(request)  # for domain

			cd = form.cleaned_data
			user = User(username=cd['username'], email=cd['email'], gender=cd['gender'])
			user.set_password(cd['confirm_password'])
			user.user_role = user_role
			user.is_active = False    # set as deactivated unless email confirmed...
			user.save()

			# create profile model associated with user
			user_profile = self.model(user=user)
			user_profile.save()

			message = render_to_string('accounts/emails/activate_account_mail.html', {
				'user': user,
				'protocol': 'http',
				'domain': site.domain,
				'uid': urlsafe_base64_encode(force_bytes(user.pk)),
				'token': account_activation_token.make_token(user)
			})

			message = Mail(
				from_email='adilsaleem1398@gmail.com',
				to_emails=[user.email],
				subject=f'Activate account for {site.domain}',
				html_content=message
			)

			try:
				sg_client = SendGridAPIClient('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')
				response = sg_client.send(message)
				messages.add_message(request, messages.SUCCESS, 'A verification email has been sent.')
				messages.add_message(request, messages.WARNING, 'Please also check your SPAM inbox!')
			except Exception as e:
				print(e)
				messages.add_message(request, messages.WARNING, str(e))

			if user:
				login(self.request, user)

			if user_role == 'S':
				save_courses_from_cookies_to_order(request, user_profile)

			if self.next_url:
				return redirect(self.next_url)
			return redirect('home')
		return self.render_to_response({'form': form})

# NO NEED TO USE THIS VIEW FOR NOW, I'LL REFACTOR THIS LATER...
class ProfileUpdateView(TemplateResponseMixin, View):
	template_name = 'accounts/authentications/profile_form.html'

	def get(self, request, *args, **kwargs):
		if request.user.user_role == 'S':
			form = StudentProfileSettingForm(request.user ,request.POST or None, request.FILES or None, instance=request.user.student_profile)

		elif request.user.user_role == 'I':
			form = IntructorProfileSettingForm(request.user ,request.POST or None, request.FILES or None, instance=request.user.instructor_profile)

		return self.render_to_response({'form': form})

	def post(self, request, *args, **kwargs):
		if request.user.user_role == 'S':
			form = StudentProfileSettingForm(request.user ,request.POST, request.FILES, instance=request.user.student_profile)

		elif request.user.user_role == 'I':
			form = IntructorProfileSettingForm(request.user ,request.POST, request.FILES, instance=request.user.instructor_profile)

		if form.is_valid():
			form.save()
			cd = form.cleaned_data
			request.user.username = cd['username']
			request.user.email = cd['email']
			request.user.first_name = cd['first_name']
			request.user.last_name = cd['last_name']
			request.user.save()

			if request.user.user_role =='S':
				return redirect('student_dashboard', request.user.student_profile.id)

			return redirect('home')
# ============================================================================================

class GeneralProfileSettingsUpdateView(CsrfExemptMixin, JsonRequestResponseMixin, View):
	def post(self, request, *args, **kwargs):
		if 'user_data' in request.POST:
			new_data = json.loads(request.POST['user_data'])
			request.user.email = new_data['email']
			request.user.first_name = new_data['firstname']
			request.user.last_name = new_data['lastname']
			request.user.save()

			response = {
				'username': request.user.username,
				'firstname': request.user.first_name,
				'lastname': request.user.last_name,
				'email': request.user.email
			}

			return self.render_json_response(response)
		return self.render_json_response({'message':'Something went wrong while updating'})

class ProfileUpdationView(CsrfExemptMixin, JsonRequestResponseMixin, View):
	def post(self, request, *args, **kwargs):
		if 'image_file' in request.FILES:
			filename = request.FILES['image_file'].name
			file_object = File(request.FILES['image_file'])			
			request.user.profile_image.save(filename, file_object)
		return self.render_json_response({})

class PasswordChangeView(TemplateResponseMixin, View):
  model = User
  template_name = 'accounts/authentications/password_change_form.html'

  def get(self, request, *args, **kwargs):
    form = PasswordChangeForm(request.user)
    return self.render_to_response({'form': form})

  def post(self, request, *args, **kwargs):
    form = PasswordChangeForm(request.user, request.POST)
    if form.is_valid():
      form.save()
      return redirect('login')