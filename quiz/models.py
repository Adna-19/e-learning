from django.db import models
from django.utils.text import slugify
from django.core.exceptions import ValidationError
from django.utils import timezone
from courses.fields import OrderField
from courses.models import Course, Module

class Quiz(models.Model):
  title          = models.CharField(max_length=200)
  teacher        = models.ForeignKey('accounts.InstructorProfile', 
                                      related_name='created_quizzes', 
                                      on_delete=models.CASCADE)
  course         = models.ForeignKey(Course, related_name='quizzes', on_delete=models.CASCADE)
  module         = models.OneToOneField(Module, related_name='attached_quiz', on_delete=models.CASCADE, null=True, blank=True)
  slug           = models.SlugField(max_length=200, unique=True, blank=True)
  score          = models.PositiveIntegerField(null=True, blank=True)
  date_created   = models.DateTimeField(auto_now_add=True)
  date_updated   = models.DateTimeField(auto_now=True)

  def clean(self):
    if not len(self.title) > 20:
      raise ValidatioError({
        'title': 'Title should have at least 20 letters'
      })

  def save(self, *args, **kwargs):
    self.slug = f"{slugify(self.title)}-{slugify(timezone.now())}"
    self.full_clean()
    super(Quiz, self).save(*args, **kwargs)

  def get_absolute_url(self):
    return f"/quizzes/{self.slug}/quiz/"

  def __str__(self):
    return f"| {self.title} || by {self.teacher.user.full_name}"

  class Meta:
    verbose_name_plural = 'Quizzes'

class Question(models.Model):
  quiz         = models.ForeignKey(Quiz, related_name='questions', on_delete=models.CASCADE)
  text         = models.CharField(max_length=400)
  is_active    = models.BooleanField(default=True)
  date_created = models.DateTimeField(auto_now_add=True)
  date_updated = models.DateTimeField(auto_now=True)
  order        = OrderField(null=True, blank=True, for_fields=['quiz'])

  def __str__(self):
    return f"Q: '{self.text}' from Quiz '{self.quiz.title}'"

  class Meta:
    ordering = ['order']

class Answer(models.Model):
  question     = models.ForeignKey(Question, related_name='answers', on_delete=models.CASCADE)
  text         = models.CharField(max_length=200)
  is_correct   = models.BooleanField(default=False)
  is_active    = models.BooleanField(default=True)
  date_created = models.DateTimeField(auto_now_add=True)
  date_updated = models.DateTimeField(auto_now=True)

  def __str__(self):
    return f"Answer: {self.text} for Q: {self.question.text}"

class TakenQuiz(models.Model):
  student = models.ForeignKey('accounts.StudentProfile', 
                              related_name='taken_quizzes', 
                              on_delete=models.CASCADE)
  quiz           = models.ForeignKey(Quiz, on_delete=models.CASCADE)
  obtained_marks = models.PositiveIntegerField(null=True, blank=True)

  def __str__(self):
    return f"Quiz: {self.quiz.title} taken by {self.student.user.full_name}"

class StudentAnswer(models.Model):
  student    = models.ForeignKey('accounts.StudentProfile', related_name='quiz_answers', on_delete=models.CASCADE, null=True, blank=True)
  answer     = models.ForeignKey(Answer, on_delete=models.CASCADE)

  def __str__(self):
    return f"Answer: {self.answer.text} by {self.student.user.full_name} {self.answer.is_correct}"