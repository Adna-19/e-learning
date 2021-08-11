from django.db import models
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey
from django.utils.translation import ugettext_lazy as _
from django.utils.text import slugify
from django.utils import timezone
from django.core.validators import MinValueValidator, MaxValueValidator
from ckeditor.fields import RichTextField
from .fields import OrderField

class Subject(models.Model):
  name = models.CharField(max_length=100)
  code = models.CharField(max_length=10)
  slug = models.SlugField(max_length=200, unique=True, null=True, blank=True)

  def save(self, *args, **kwargs):
    self.slug = slugify(self.name)
    super(Subject, self).save(*args, **kwargs)

  def __str__(self):
    return self.name

  class Meta:
    ordering = ['name']

class CourseManager(models.Manager):
  def paid_courses(self):
    return self.filter(payment_status='paid', trashed=False).order_by('-date_created')

  def free_courses(self):
    return self.filter(payment_status='free', trashed=False).order_by('-date_created')

  def completed_courses(self, student):
    return [acheivement.course for acheivement in student.achievements.all().order_by('-date_created')]

  def enrolled_courses(self, student, payment_status=None):
    if not payment_status:
      qs = self.filter(students__in=[student]).order_by('-date_created')
      return [course for course in qs if course not in self.completed_courses(student)]

    courses = self.filter(students__in=[student], payment_status=payment_status).order_by('-date_created')
    return [course for course in courses if course not in  self.completed_courses(student)]

  def latest_activity(self, student):
    latest_activities = []
    
    for course in self.enrolled_courses(student):
      continued_course = any([student in module.students_viewed.all() for module in course.modules.all()])
      student_achievements = [acheivement.course for acheivement in student.achievements.all()]

      if continued_course and course not in student_achievements:
        latest_activities.append(course)

    return latest_activities

class Course(models.Model):
  PAYMENT_STATUS = (
    ('free', 'Free'),
    ('paid', 'Paid'),
  )

  title          = models.CharField(max_length=200)
  subject        = models.ForeignKey(Subject, related_name='courses', on_delete=models.CASCADE)  
  instructor     = models.ForeignKey('accounts.InstructorProfile', related_name='courses', on_delete=models.CASCADE)
  image          = models.ImageField(upload_to='course_images/', null=True)
  slug           = models.SlugField(max_length=200, unique=True, null=True, blank=True)
  students       = models.ManyToManyField('accounts.StudentProfile')
  description    = models.TextField()
  requirements   = models.TextField(null=True, blank=True)
  trashed        = models.BooleanField(default=False)
  payment_status = models.CharField(max_length=5, choices=PAYMENT_STATUS)
  price          = models.DecimalField(max_digits=4, decimal_places=2, default=0.00)
  date_created   = models.DateTimeField(auto_now_add=True)
  date_updated   = models.DateTimeField(auto_now=True)

  objects = CourseManager()

  def get_current_rating(self):
    ratings = {}
    for rating_value in range(1, 6):
      try:
        rating_counts = self.student_reviews.filter(rating=rating_value).count()
        ratings[rating_value] = rating_counts
      except:   pass     
    current_rating = max(ratings, key=ratings.get)
    return current_rating

  def percent_completed(self, student):
    completed_modules = self.modules.filter(students_viewed__in=[student]).count()
    total_modules = self.modules.count()
    return round((completed_modules/total_modules) * 100)

  def get_absolute_url(self):
    return f"/course/{self.slug}/details/"

  def save(self, *args, **kwargs):
    self.slug = f"{slugify(self.title)}-{slugify(str(self.date_created))}"
    super(Course, self).save(*args, **kwargs)

  def __str__(self):
    return f"{self.title} created by {self.instructor.user.username}"

class Acheivement(models.Model):
  student = models.ForeignKey('accounts.StudentProfile', related_name='achievements', on_delete=models.CASCADE)
  course = models.ForeignKey(Course, related_name='achievements', on_delete=models.CASCADE)
  certificate = models.FileField(null=True, blank=True)
  date_created = models.DateTimeField(auto_now_add=True)

  def __str__(self):
    return f"Achievment by {self.student.user.username} on {self.course.title}"

class Order(models.Model):
  customer       = models.ForeignKey('accounts.StudentProfile', on_delete=models.CASCADE)
  date_ordered   = models.DateTimeField(auto_now_add=True)
  complete       = models.BooleanField(default=False)
  transaction_id = models.CharField(max_length=200, null=True)

  @property
  def get_total_cart_price(self):
    ordered_courses  = [item.course for item in self.orderitem_set.all()]
    total_cart_price = sum([course.price for course in ordered_courses])
    return total_cart_price

  @property
  def get_cart_items(self):
    return self.orderitem_set.count()

  def __str__(self):
    return str(self.id)

class OrderItem(models.Model):
  course     = models.ForeignKey(Course, on_delete=models.SET_NULL, blank=True, null=True)
  order      = models.ForeignKey(Order, on_delete=models.SET_NULL, blank=True, null=True)
  date_added = models.DateTimeField(auto_now_add=True)

  def __str__(self):
    return self.course.title

class Module(models.Model):
  title     = models.CharField(max_length=100)
  course    = models.ForeignKey(Course, related_name='modules', on_delete=models.CASCADE)
  summary   = models.TextField()
  students_viewed = models.ManyToManyField('accounts.StudentProfile', blank=True)
  slug      = models.SlugField(max_length=200, unique=True, null=True, blank=True)
  order     = OrderField(blank=True, for_fields=['course'])

  class Meta:
    ordering = ['order']

  def get_absolute_url(self):
    return f"/course/module/{self.slug}/contents/"

  def save(self, *args, **kwargs):
    self.slug = f"{slugify(self.title)}-{slugify(timezone.now())}"
    super(Module, self).save(*args, **kwargs)

  def __str__(self):
    return f"{self.order}. {self.title}"

class Content(models.Model):
  module          = models.ForeignKey(Module, related_name='contents', on_delete=models.CASCADE)
  order           = OrderField(blank=True, for_fields=['module'])
  students_viewed = models.ManyToManyField('accounts.StudentProfile', blank=True)
  
  # mandatory fields for generic relationship
  content_type   = models.ForeignKey(ContentType, on_delete=models.CASCADE, limit_choices_to={'model__in': ('text', 'video', 'image', 'file')})
  object_id      = models.PositiveIntegerField()
  content_object = GenericForeignKey()

  class Meta:
    ordering = ['order']

class BaseContent(models.Model):
  title        = models.CharField(max_length=200)
  owner        = models.ForeignKey('accounts.InstructorProfile', related_name='%(class)s_related', on_delete=models.CASCADE)
  date_created = models.DateTimeField(auto_now_add=True)
  date_updated = models.DateTimeField(auto_now_add=True)
 
  class Meta:
    abstract = True

  def __str__(self):
    return self.title

class Text(BaseContent):
  text = models.TextField()

class Video(BaseContent):
  video = models.FileField(upload_to='content_videos/')

class Image(BaseContent):
  image = models.FileField(upload_to='content_images/')

class File(BaseContent):
  file = models.FileField(upload_to='content_files/')

# NOTIFICATION SYSTEM IMPLEMENTATION
class ContentTypeToGetModel(object):

  def get_related_object(self):
    model_class = self.content_type.model_class()
    return model_class.objects.get(id=self.object_id)

  @property
  def _model_name(self):
    return self.get_related_object()._meta.model_name

class Review(models.Model):
  course = models.ForeignKey(Course, related_name='student_reviews', on_delete=models.CASCADE)
  user   = models.ForeignKey('accounts.User', related_name='given_reviews', on_delete=models.CASCADE)
  rating  = models.PositiveIntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
  comment = models.TextField()
  date_created = models.DateTimeField(auto_now_add=True)

  def __str__(self):
    return f"Review by {self.user.full_name} on {self.course.title}"

class Notification(models.Model, ContentTypeToGetModel):
  STATUS_CHOICES = (
    ('review', 'a review'),
    ('comment', 'a comment'),
    ('reply', 'a reply'),
    ('enrolling', 'an enrolling')
  )

  sender       = models.ForeignKey('accounts.User', 
                                related_name='sent_notifications', 
                                on_delete=models.CASCADE)
  receiver     = models.ForeignKey('accounts.User', 
                                related_name='received_notifications', 
                                on_delete=models.CASCADE)

  created      = models.DateTimeField(auto_now_add=True)
  status       = models.CharField(max_length=60, choices=STATUS_CHOICES, default='review')
  seen         = models.BooleanField(default=False)
  
  content_type = models.ForeignKey(ContentType, related_name='notifications', on_delete=models.CASCADE)
  object_id      = models.PositiveIntegerField()
  content_object = GenericForeignKey('content_type', 'object_id')

  def __str__(self):
    return f"given a {self.status}"

  class Meta:
    ordering = ['-created']