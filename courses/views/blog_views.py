from braces.views import CsrfExemptMixin, JsonRequestResponseMixin
from django.views.generic.list import ListView
from blog.models import Post
from blog.forms import PostForm

class CMSPostListView(ListView):
  model = Post 
  context_object_name = 'posts'
  paginate_by   = 12
  template_name = 'courses/manage/blog/blog_home.html'

  def get_queryset(self):
    qs = super().get_queryset()
    return qs.filter(author=self.request.user, trashed=False).order_by('-date_created')

  def get_context_data(self, **kwargs):
    context = super().get_context_data(**kwargs)
    context['post_form'] = PostForm
    context['trash_count'] = self.request.user.posts.filter(trashed=True).count()
    return context