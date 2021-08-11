from django.views.generic import ListView, DetailView
from django.views.generic.base import TemplateResponseMixin, View
from django.contrib.auth.mixins import LoginRequiredMixin
from braces.views import CsrfExemptMixin, JsonRequestResponseMixin
from ..models import Notification

class NotificationListView(ListView):
	model = Notification
	context_object_name = 'notifications'
	paginate_by = 10
	template_name = 'courses/notifications.html'

	def get_queryset(self):
		notifications = self.model.objects.filter(receiver=self.request.user)
		notifications.update(seen=True) # marked as read
		return notifications

	def get_context_data(self, **kwargs):
		context = super().get_context_data(**kwargs)
		context['base_template'] = 'cms_base.html' if self.request.user.user_role == 'I' else 'classroom_base.html'
		return context

class NotificationDetailView(DetailView):
	model = Notification
	context_object_name = 'notification'
	template_name = 'courses/notification_detail.html'

	def get_context_data(self, **kwargs):
		context = super().get_context_data(**kwargs)
		context['base_template'] = 'cms_base.html' if self.request.user.user_role == 'I' else 'classroom_base.html'
		return context
