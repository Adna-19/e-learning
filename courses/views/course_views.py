from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views.generic.list import ListView
from django.views.generic.base import RedirectView, View, TemplateResponseMixin
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from braces.views import CsrfExemptMixin, JsonRequestResponseMixin
from django.contrib import messages
from django.core.cache import cache
from datetime import datetime
from django.utils import timezone
from ..utils import time_greeting_message, get_weather_updates
from ..models import *

class CMSHomePageView(PermissionRequiredMixin, LoginRequiredMixin, TemplateResponseMixin, View):
  template_name = 'courses/manage/course/cms_home.html'
  permission_required = 'courses.view_course'

  def get_weather_updates_from_api_or_cache(self):
    # weather_details = cache.get('weather_data')
    # if not weather_details:
    #   weather_details = get_weather_updates('Dera Ismail Khan')
    #   cache.set('weather_data', weather_details)
    # return weather_details
    return get_weather_updates('Dera Ismail Khan')

  def get(self, request, *args, **kwargs):
    greeting_message = time_greeting_message(datetime.now().hour)
    weather_details  = self.get_weather_updates_from_api_or_cache()
    latest_courses   = Course.objects.filter(
                        instructor__user=request.user,
                        trashed=False
                      ).order_by('-date_created')[:3]

    return self.render_to_response({
      'greeting_message': greeting_message,
      'today': timezone.now().date,
      'weather_details': weather_details,
      'latest_courses': latest_courses
    })

class ManageCourseListView(PermissionRequiredMixin, LoginRequiredMixin, ListView):
  model = Course 
  template_name = 'courses/manage/course/course_list.html'
  context_object_name = 'courses'
  paginate_by = 3
  permission_required = 'courses.view_course'

  def get_queryset(self):
    qs = super().get_queryset()
    return qs.filter(instructor__user=self.request.user, trashed=False).order_by('-date_created')
    
class CourseCreateView(PermissionRequiredMixin, LoginRequiredMixin, CreateView):
  model = Course
  template_name = 'courses/manage/course/course_form.html'
  fields = ('subject', 'image', 'title', 'description', 'payment_status', 'price')
  success_url = reverse_lazy('manage_course_list')
  permission_required = 'courses.add_course'
  
  def form_valid(self, form):
    form.instance.instructor = self.request.user.instructor_profile
    messages.success(self.request, 'Course created successfully')
    return super(CourseCreateView, self).form_valid(form)

class CourseUpdateView(PermissionRequiredMixin, LoginRequiredMixin, UpdateView):
  model = Course
  template_name = 'courses/manage/course/course_form.html'
  fields = ('subject', 'image', 'title', 'description', 'payment_status', 'price')
  success_url = reverse_lazy('manage_course_list')
  permission_required = 'courses.change_course'

  def form_valid(self, form):
    messages.success(self.request, 'Course updated successfully')
    return super(CourseUpdateView, self).form_valid(form)

class CMSTrashListView(PermissionRequiredMixin, LoginRequiredMixin, TemplateResponseMixin, View):
  template_name = 'courses/manage/course/trash.html'
  permission_required = 'courses.change_course'

  def get(self, request, *args, **kwargs):
    trashed_courses = request.user.instructor_profile.courses.filter(trashed=True)
    return self.render_to_response({
      'trashed_courses': trashed_courses
    })

class CourseTrashedUntrashedView(
  PermissionRequiredMixin, 
  LoginRequiredMixin, 
  CsrfExemptMixin, 
  JsonRequestResponseMixin , View):
  permission_required = 'courses.delete_course'

  def get(self, request, *args, **kwargs):
    instructor_courses = request.user.instructor_profile.courses.all()
    course = instructor_courses.get(slug=kwargs['course_slug'])

    if kwargs['action'] == 'delete':
      course.trashed = True
    elif kwargs['action'] == 'restore':
      course.trashed = False
    
    course.save()

    return self.render_json_response({
      'message': 'Course Trashed...' if kwargs['action'] == 'delete' else 'Course Restored...',
      'course_id': course.id 
    })

class TrashEmptyingView(PermissionRequiredMixin, LoginRequiredMixin, RedirectView):
  permanent = False
  query_string = True
  pattern_name = 'manage_course_list'
  permission_required = 'courses.delete_course'

  def get_redirect_url(self, *args, **kwargs):
    trashed_courses = self.request.user.instructor_profile.courses.filter(trashed=True)
    [course.delete() for course in trashed_courses]
    return super().get_redirect_url(*args, **kwargs)