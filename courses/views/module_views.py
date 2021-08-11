from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.views.generic.base import TemplateResponseMixin, View, RedirectView
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from braces.views import CsrfExemptMixin, JsonRequestResponseMixin, MultiplePermissionsRequiredMixin
from ..forms import ModuleForm
from ..models import Course, Module

class ModulesListView(PermissionRequiredMixin, LoginRequiredMixin, TemplateResponseMixin, View):
  template_name = 'courses/manage/module/course_modules_list.html'
  course = None
  permission_required = 'courses.view_module'

  def get(self, request, slug, *args, **kwargs):
    self.course = get_object_or_404(Course, slug=slug, instructor__user=request.user)
    return self.render_to_response({'course': self.course, 'modules':self.course.modules.all()})

class ModulesCreateUpdateView(MultiplePermissionsRequiredMixin, LoginRequiredMixin, TemplateResponseMixin, View):
  template_name = 'courses/manage/module/module_formset.html'
  course = None
  permissions = {"all": ("courses.add_module", "courses.change_module")}

  def dispatch(self, request, slug, *args, **kwargs):
    self.course = get_object_or_404(Course, slug=slug, instructor__user=request.user)
    return super(ModulesCreateUpdateView, self).dispatch(request, slug, *args, **kwargs)

  def get(self, request, slug, *args, **kwargs):
    form = ModuleForm(data=None)
    return self.render_to_response({'course':self.course, 'form':form})

  def post(self, request, slug, *args, **kwargs):
    form = ModuleForm(data=request.POST)
    if form.is_valid() and not request.is_ajax():
      new_module = form.save(commit=False)
      new_module.course = self.course
      new_module.save()
      return redirect('modules_list', self.course.slug)
    return self.render_to_response({'course':self.course, 'form':form})

class ModuleDeleteView(PermissionRequiredMixin, LoginRequiredMixin, View):
  permission_required = "courses.delete_module"

  def get(self, request, slug, *args, **kwargs):
    if request.is_ajax:
      module = get_object_or_404(Module, slug=slug)
      module.delete()
      return JsonResponse({'message': 'Module deleted successfully'})
    return JsonResponse({})

class ModuleOrderView(CsrfExemptMixin, JsonRequestResponseMixin, View):
  def post(self, request, *args, **kwargs):
    for object_id, order in self.request_json.items():
      Module.objects.filter(
        id=int(object_id), 
        course__instructor__user=request.user
      ).update(order=order)
    return self.render_json_response({'message': 'Reordered successfully'})