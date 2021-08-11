from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.views.generic.base import TemplateResponseMixin, View, RedirectView
from django.views.generic.list import ListView
from django.views.generic.detail import DetailView
from braces.views import CsrfExemptMixin, JsonRequestResponseMixin
from django.core.files import File
from courses.models import Notification
from django.contrib.contenttypes.models import ContentType
from django.utils.dateformat import format
from .models import Post, Category, Comment, CommentReply
from .forms import PostForm
from accounts.models import User
import json

class PostListView(ListView):
	model = Post 
	context_object_name = 'posts'
	paginate_by   = 2
	template_name = 'blog/posts_list.html'

	def get_queryset(self):
		qs = super().get_queryset()
		return qs.filter(status='published')

	def get_context_data(self, **kwargs):
		context = super().get_context_data(**kwargs)
		context['categories'] = Category.objects.all()
		return context

class PostDetailView(DetailView):
	model = Post
	context_object_name = 'post'
	template_name = 'blog/post_details.html'

	def get_context_data(self, **kwargs):
		context = super().get_context_data(**kwargs)
		context['categories'] = Category.objects.all()
		return context

class PostCommentView(CsrfExemptMixin, JsonRequestResponseMixin, View):
	def post(self, request, post_slug, *agrs, **kwargs):
		post = get_object_or_404(Post, slug=post_slug)
		if post and request.user.is_authenticated:
			new_comment = Comment(post=post, user=request.user, content=request.POST['content'])
			new_comment.save()
			response = {
				'id': new_comment.id,
				'comment': new_comment.content,
				'username': request.user.full_name,
				'profile_image': request.user.profile_image.url,
				'date_created': new_comment.date_created,
				'message': 'Comment added successfully'
			}

			# send notification to post author
			Notification.objects.create(
				receiver=post.author,
				sender=request.user,
				content_type=ContentType.objects.get(app_label='blog', model='comment'),
				object_id=new_comment.id,
				status='comment'
			)

			return self.render_json_response(response)
		
		return self.render_json_response({
			'message': 'Something wents wronge'
		})

class CommentReplyView(CsrfExemptMixin, JsonRequestResponseMixin, View):
	def post(self, request, comment_id, *args, **kwargs):
		comment = get_object_or_404(Comment, id=comment_id)

		reply_user = User.objects.get(id=request.POST['reply_user_id']) if 'reply_user_id' in request.POST else None

		if comment and request.user.is_authenticated:
			reply = CommentReply(
				reply_to=comment,
				reply_by=request.user,
				content=request.POST['reply'],
			)
			reply.save()

			# sending notification to the person who commented
			Notification.objects.create(
				receiver=reply_user if reply_user else comment.user,
				sender=request.user,
				content_type=ContentType.objects.get(app_label='blog', model='commentreply'),
				object_id=reply.id,
				status='reply'
			)

			response = {
				'reply_id': reply.id,
				'profile_image': reply.reply_by.profile_image.url,
				'full_name': reply.reply_by.full_name,
				'date_created': reply.date_created,
				'content': reply.content,
				'message': 'successfully added reply'
			}
			return self.render_json_response(response, status=200)
		return self.render_json_response({'message': 'Something went wrong'}, status=404)

class CommentDeleteView(JsonRequestResponseMixin, View):
	def get(self, request, comment_id, *args, **kwargs):
		comment = get_object_or_404(Comment, id=comment_id, user=request.user)

		if request.user.is_authenticated and request.user == comment.user:
			comment.delete()
			return JsonResponse({'message': 'deleted successfully'}, status=200)
		
		return JsonResponse({'messsage': 'Something went wrong'}, status=400)

class CommentReplyDeleteView(JsonRequestResponseMixin, View):
	def get(self, request, comment_id, reply_id, *args, **kwargs):
		comment = get_object_or_404(Comment, id=comment_id)

		if request.user.is_authenticated:
			reply = comment.replies.get(id=reply_id)
			if reply.reply_by == request.user:
				reply.delete()
			return JsonResponse({'message': 'deleted successfully'}, status=200)
		
		return JsonResponse({'messsage': 'Something went wrong'}, status=400)

class ArticleCreateView(CsrfExemptMixin, JsonRequestResponseMixin, View):
	def post(self, request, *args, **kwargs):
		data = json.loads(request.POST['post_data'])
		data['category'] = Category.objects.get(id=int(data['category']))
		form = PostForm(data, request.FILES)

		if form.is_valid() and request.method == 'POST':
			new_post = form.save(commit=False)
			new_post.author = request.user
			new_post.save()

		return self.render_json_response({'message': 'POST DATA SUBMITTED...'})

class ArticleUpdateView(TemplateResponseMixin, View):
	template_name = 'courses/manage/blog/post_edit.html'

	def get(self, request, post_slug, *args, **kwargs):
		post = request.user.posts.get(slug=post_slug)
		form = PostForm(request.POST or None, request.FILES or None, instance=post)

		return self.render_to_response({
			'form': form,
			'post': post
		})

	def post(self, request, post_slug, *args, **kwargs):
		post = request.user.posts.get(slug=post_slug)
		form = PostForm(request.POST, request.FILES, instance=post)

		if form.is_valid():
			form.save()
			return redirect('cms_blog')
		return self.render_to_response({'form': form, 'post': post})

class TrashUnTrashArticle(CsrfExemptMixin, JsonRequestResponseMixin, View):
	def get(self, request, *args, **kwargs):
		post = request.user.posts.get(slug=kwargs['post_slug'])
		action = kwargs['action']
		
		if action == 'delete':
			post.trashed = True
		elif action == 'restore':
			post.trashed = False

		post.save()
		return self.render_json_response({
			'message': 'Moved to trash' if action == 'delete' else 'Restored from Trash',
			'post_id': post.id,
			'action': action
		})

class EmptyBlogTrashView(RedirectView):
	permanent = False
	query_string = True
	pattern_name = 'cms_blog'

	def get_redirect_url(self, *args, **kwargs):
		posts = self.request.user.posts.filter(trashed=True)
		[post.delete() for post in posts if post.author == self.request.user]
		return super().get_redirect_url(*args, **kwargs)

class TrashListView(CsrfExemptMixin, JsonRequestResponseMixin, View):
	def get(self, request, *args, **kwargs):
		trashed_posts = request.user.posts.filter(trashed=True)
		results = []

		for post in trashed_posts:
			item = {
				'id': post.id,
				'title': post.title,
				'summary': f"{post.summary[:180]}...",
				'date_created': format(post.date_created, 'M, d Y'),
				'author': request.user.username,
				'slug': post.slug,
				'image': post.image.url
			}
			results.append(item)
		return self.render_json_response(results)