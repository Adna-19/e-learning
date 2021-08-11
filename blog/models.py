from django.db import models
from django.utils.text import slugify
from django.utils import timezone
from ckeditor_uploader.fields import RichTextUploadingField
from accounts.models import User
from taggit.managers import TaggableManager

class Category(models.Model):
	title = models.CharField(max_length=100)
	slug = models.SlugField(max_length=200, unique=True, null=True, blank=True)

	def save(self, *args, **kwargs):
		self.slug = f"{slugify(self.title)}-{slugify(timezone.now())}"
		super(Category, self).save(*args, **kwargs)

	def __str__(self):
		return self.title

	class Meta:
		verbose_name_plural = 'Categories'

class PostManager(models.Manager):
	def published(self):
		return self.filter(status='published').order_by('-date_published')

	def comments_greater_than(self, value):
		posts = self.filter(status='published').order_by('-date_published')
		most_commented_posts = []
		for post in posts:
			if post.comments.count() >= value:
				most_commented_posts.append(post)
		return most_commented_posts

class Post(models.Model):
	STATUS_CHOICES = (
		('published', 'Published'),
		('draft', 'Draft'),
	)

	author   = models.ForeignKey(User, on_delete=models.SET_NULL, related_name='posts', null=True)
	category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='posts')
	title    = models.CharField(max_length=255, null=True, blank=True)
	image    = models.ImageField(upload_to='files/blog/posts/images/')
	slug     = models.SlugField(max_length=200, unique=True, null=True, blank=True)
	content  = RichTextUploadingField() 
	summary  = models.TextField()
	status   = models.CharField(max_length=10, choices=STATUS_CHOICES)
	trashed = models.BooleanField(default=False)
	date_created   = models.DateField(auto_now_add=True)
	date_updated   = models.DateField(auto_now=True)
	date_published = models.DateField()

	tags    = TaggableManager()
	objects = PostManager()

	def save(self, *args, **kwargs):
		self.slug = f"{slugify(self.title)}-{slugify(timezone.now())}"
		super(Post, self).save(*args, **kwargs)

	def get_absolute_url(self):
		return f"/blog/post/{self.slug}/details"

	def __str__(self):
		return self.title

class Comment(models.Model):
	post         = models.ForeignKey(Post, related_name='comments', on_delete=models.CASCADE)
	user 		 = models.ForeignKey(User, null=True, related_name='comments', on_delete=models.CASCADE) 
	content      = models.TextField()
	active       = models.BooleanField(default=True)
	date_created = models.DateField(auto_now_add=True)
	date_updated = models.DateField(auto_now=True)

	def __str__(self):
		return f"{self.user.username} comment on {self.post.title}"

class CommentReply(models.Model):
	reply_to = models.ForeignKey(Comment, related_name='replies', on_delete=models.CASCADE)
	content      = models.TextField()
	reply_by     = models.ForeignKey(User, null=True, on_delete=models.CASCADE)
	active       = models.BooleanField(default=True) 
	date_created = models.DateField(auto_now_add=True)
	date_updated = models.DateField(auto_now=True)

	def __str__(self):
		return f"{self.reply_by.username} replied to {self.reply_to.user.username} on {self.reply_to}"
		
	class Meta:
		verbose_name_plural = 'Comments Replies'