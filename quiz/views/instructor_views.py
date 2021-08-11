from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponseRedirect
from django.views.generic.base import View, TemplateResponseMixin
from django.views.generic.list import ListView
from django.views.generic.detail import DetailView
from django.views.generic.edit import CreateView
from django.urls import reverse_lazy
from braces.views import CsrfExemptMixin, JsonRequestResponseMixin
from ..models import Quiz, Question
from ..forms import QuestionForm, AnswersFormSet, QuizForm

class TeacherQuizHomeView(ListView):
  template_name       = 'instructors/quizzes_list.html'
  context_object_name = 'quizzes'
  model               = Quiz
  course              = None

  def dispatch(self, request, *args, **kwargs):
    instructor = request.user.instructor_profile
    courses = instructor.courses

    self.course = courses.get(slug=kwargs['course_slug']) if 'course_slug' in kwargs else courses.first() 

    return super().dispatch(request, *args, **kwargs)

  def get_queryset(self):
    qs = super().get_queryset()
    return qs.filter(teacher__user=self.request.user, course=self.course).order_by('-date_created')

  def get_context_data(self, **kwargs):
    context = super().get_context_data(**kwargs)
    context['courses'] = self.request.user.instructor_profile.courses.all()
    context['current_course'] = self.course
    return context

class TeacherQuizDetailView(DetailView):
  model               = Quiz
  context_object_name = 'quiz'
  template_name       = 'instructors/quiz_details.html'

  def get_context_data(self, **kwargs):
    context = super().get_context_data(**kwargs)
    context['course'] = self.get_object().course
    return context

class QuizCreateUpdateView(CreateView):
  template_name = 'instructors/create_quiz.html'
  model         = Quiz
  quiz_obj      = None
  success_url   = reverse_lazy('quizzes_list')
  course        = None

  def dispatch(self, request, course_slug, id=None, *args, **kwargs):
    self.course = request.user.instructor_profile.courses.get(slug=course_slug)

    if id:
      self.quiz_obj = get_object_or_404(Quiz, id=id, teacher__user=request.user)
    return super(QuizCreateUpdateView, self).dispatch(request, id, *args, **kwargs)

  def get(self, request, id=None, *args, **kwargs):
    form = QuizForm(request.POST or None, instance=self.quiz_obj)
    return self.render_to_response({
      'form': form, 
      'object': self.quiz_obj, 
      'modules': self.course.modules.all()
    })

  def post(self, request, id=None, *args, **kwargs):
    form = QuizForm(request.POST, instance=self.quiz_obj)
    if form.is_valid() and not request.is_ajax():
      if self.quiz_obj:
        form.save()
      else:
        quiz = form.save(commit=False)
        quiz.teacher = request.user.instructor_profile
        quiz.course  = self.course
        quiz.module = self.course.modules.get(slug=request.POST['module'])
        quiz.save()
      return HttpResponseRedirect(self.success_url)
    return self.render_to_response({'form': form})

class QuizDeleteView(View):
  def get(self, request, id, *args, **kwargs):
    quiz = get_object_or_404(Quiz, id=id, teacher__user=request.user)
    quiz.delete()
    return redirect('quizzes_list')

class QuestionCreateUpdateView(CreateView):
  template_name = 'instructors/create_question.html'
  model         = Question
  quiz          = None
  success_url   = None
  question      = None

  def dispatch(self, request, pk, question_id=None, *args, **kwargs):
    self.quiz = get_object_or_404(Quiz, id=pk, teacher__user=request.user)
    self.success_url = reverse_lazy('quiz_cms_details', kwargs={'pk': self.quiz.id})

    if question_id:
      self.question = get_object_or_404(Question, id=question_id, quiz=self.quiz)
    return super(QuestionCreateUpdateView, self).dispatch(request, pk, *args, **kwargs)

  def get(self, request, pk, *args, **kwargs):
    self.object  = None
    form         = QuestionForm(request.POST or None, instance=self.question)
    answer_forms = AnswersFormSet(instance=self.question, data=None)
    return self.render_to_response(
      self.get_context_data(
        form=form, answer_forms=answer_forms, question=self.question
      )
    )

  def post(self, request, pk, *args, **kwargs):
    self.object  = None
    form         = QuestionForm(request.POST, instance=self.question)
    answer_forms = AnswersFormSet(instance=self.question, data=self.request.POST)

    if form.is_valid() and answer_forms.is_valid() and not request.is_ajax():
      return self.form_valid(form, answer_forms)
    return self.form_invalid(form, answer_forms)

  def form_valid(self, form, answer_forms):

    if self.question:
      form.save()
      answer_forms.instance = self.question
      answer_forms.save()
    else:
      question = form.save(commit=False)
      question.quiz = self.quiz
      question.save()
      self.object = question
      answer_forms.instance = self.object
      answer_forms.save()

    return redirect('quiz_cms_details', self.quiz.id)

  def form_invalid(self, form, answer_forms):
    return self.render_to_response(
      self.get_context_data(
        form=form, answer_forms=answer_forms
      )
    )

class QuestionDeleteView(View):
  def get(self, request, pk, *args, **kwargs):
    question = get_object_or_404(Question, id=pk, quiz__teacher__user=request.user)
    question.delete()
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

class OrderQuestion(CsrfExemptMixin, JsonRequestResponseMixin, View):
  def post(self, request, *args, **kwargs):
    for object_id, order in self.request_json.items():
      print(type(object_id), object_id)
      Question.objects.filter(
        id=int(object_id),
        quiz__teacher__user=request.user
      ).update(order=order)
    return self.render_json_response({'message': 'Reordered successfully'})