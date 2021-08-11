from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.views.generic.base import TemplateResponseMixin, View, RedirectView
from django.apps import apps
from django.forms.models import modelform_factory
from django.http import JsonResponse
from braces.views import CsrfExemptMixin, JsonRequestResponseMixin, MultiplePermissionsRequiredMixin
from ..models import Module, Content

class ModuleContentListView(PermissionRequiredMixin, LoginRequiredMixin, TemplateResponseMixin, View):
  template_name = 'courses/manage/content/content_list.html'
  permission_required = 'courses.view_content'

  def get(self, request, slug, *args, **kwargs):
    module = get_object_or_404(Module, slug=slug, course__instructor__user=request.user)
    return self.render_to_response({
      'modules_list': Module.objects.filter(course=module.course, course__instructor__user=request.user),
      'module': module, 'contents': module.contents.all()})

class ContentCreateUpdateView(MultiplePermissionsRequiredMixin, LoginRequiredMixin, TemplateResponseMixin, View):
  template_name = 'courses/manage/content/content_form.html'
  model = None
  module = None
  obj = None
  permissions = {"all":("courses.add_content", "courses.change_content")}

  def get_content_model(self, model_name):
    if model_name in ('text', 'video', 'image', 'file', 'quiz'):
      return apps.get_model(app_label='courses', model_name=model_name)
    return None

  def get_form(self, model, *args, **kwargs):
    Form = modelform_factory(model, exclude=['owner', 'order', 'date_created', 'date_updated'])
    return Form(*args, **kwargs)

  def dispatch(self, request, slug, model_name, id=None, *args, **kwargs):
    self.module = get_object_or_404(Module, slug=slug, course__instructor__user=request.user)
    self.model = self.get_content_model(model_name)
    
    if id:
      self.obj = get_object_or_404(self.model, id=id, owner=request.user.instructor_profile)
    return super(ContentCreateUpdateView, self).dispatch(request, slug, model_name, id, *args, **kwargs)

  def get(self, request, slug, model_name, id=None, *args, **kwargs):
    form = self.get_form(self.model, instance=self.obj)
    return self.render_to_response({'form':form, 'object':self.obj})

  def post(self, request, slug, model_name, id=None, *args, **kwargs):
    form = self.get_form(self.model, instance=self.obj, data=request.POST, files=request.FILES)

    if form.is_valid() and not request.is_ajax():
      content = form.save(commit=False)
      content.owner = request.user.instructor_profile
      content.save()
      if not id:
        Content.objects.create(module=self.module, content_object=content)
      return redirect('content_list', self.module.slug)
    return self.render_to_response({'form':form, 'object':self.obj})

class ContentDeleteView(PermissionRequiredMixin, LoginRequiredMixin, View):
  permission_required = "courses.delete_content"
  
  def get_content_model(self, model_name):
    if model_name in ('text', 'video', 'image', 'file'):
      return apps.get_model(app_label='courses', model_name=model_name)
    return None

  def get(self, request, slug, model_name, id, *args, **kwargs):
    if request.is_ajax:
      module = get_object_or_404(Module, slug=slug, course__instructor__user=request.user)
      model = self.get_content_model(model_name)
      
      content = module.contents.get(id=id, content_type__model=model_name)
      content_item = get_object_or_404(model, id=content.content_object.id, owner=request.user.instructor_profile)
      
      # delete both content and content_item
      content.delete();   content_item.delete()
      return JsonResponse({'message':'Content Deleted Successfully'})
    return JsonResponse({'message':'Something wents wrong'})

class ContentOrderView(CsrfExemptMixin, JsonRequestResponseMixin, View):
  def post(self, request, *args, **kwargs):
    for object_id, order in self.request_json.items():
      Content.objects.filter(
        id=int(object_id), 
        module__course__instructor__user=request.user
      ).update(order=order)
    return self.render_json_response({'message': 'Reordered successfully'})