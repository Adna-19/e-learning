from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponseRedirect, HttpResponse
from django.views.generic.base import View, TemplateResponseMixin
from django.contrib import messages
from braces.views import CsrfExemptMixin, JsonRequestResponseMixin
from quiz.models import *
import json
from ..utils import remove_previous_progress

class StudentHomeView(TemplateResponseMixin, View):
  template_name = 'students/home.html'
  interest_subjects = None
  subjects = None
  
  def dispatch(self, request, *args, **kwargs):
    self.interest_subjects = request.user.student_profile.interests
    if not self.interest_subjects.all():
      self.subjects = Subject.objects.all()
    return super(StudentHomeView, self).dispatch(request, *args, **kwargs)

  def get(self, request, *args, **kwargs):
    quizzes = Quiz.objects.all()
    taken_quizzes = request.user.student_profile.taken_quizzes.all()
    trending_five = Quiz.objects.all().order_by('-date_created')[:5]
    return self.render_to_response({
      'subjects': self.subjects, 
      'quizzes': quizzes,
      'taken_quizzes': taken_quizzes,
      'trending_five': trending_five,
      'top_three_teacers': [],# TeacherProfile.objects.top_three_quiz_creators()
    })

  def post(self, request, *args, **kwargs):
    selected_subjects_slugs = [slug for slug in list(request.POST.values())[1:]]
    if selected_subjects_slugs:
      for subject_slug in selected_subjects_slugs:
        subject = self.subjects.get(slug=subject_slug)
        if subject not in self.interest_subjects.all():
          self.interest_subjects.add(subject)        
    return self.render_to_response({'message': 'Subjects Selected successfullyy'})

class StudentQuizDetailView(TemplateResponseMixin, View):
  template_name = 'students/details.html'
  obtained_marks = None

  def get(self, request, pk, *args, **kwargs):
    quiz        = get_object_or_404(Quiz, id=pk)
    total_marks = sum([question.score for question in quiz.questions.all()])
    student     = request.user.student_profile
    
    if student.taken_quizzes.filter(quiz=quiz).exists():
      self.obtained_marks = student.taken_quizzes.get(quiz=quiz).obtained_marks

    related_quizzes = Quiz.objects.filter(subject=quiz.subject).exclude(title=quiz.title).order_by('-date_created')[:5]

    return self.render_to_response({
      'quiz': quiz, 
      'obtained_marks': self.obtained_marks, 
      'total_marks':total_marks,
      'related_quizzes': related_quizzes
    })

class StudentQuizAttemptView(CsrfExemptMixin, JsonRequestResponseMixin, View):

  def post(self, request, quiz_id, *args, **kwargs):
    quiz     = get_object_or_404(Quiz, id=quiz_id)
    student  = request.user.student_profile
    taken_quizzes = [taken_object.quiz for taken_object in student.taken_quizzes.all()]

    if quiz in taken_quizzes:
      # if quiz already attempted, delete previous progress and re-attempt.
      remove_previous_progress(student, quiz)

    question_answers = json.loads(request.POST['question_answers'])

    for question_id, answer_id in question_answers.items():
      question = quiz.questions.get(id=int(question_id))
      answer = question.answers.get(id=int(answer_id))
      StudentAnswer.objects.create(student=student, answer=answer)

    total_marks = quiz.score 
    obtained_marks = student.quiz_answers.filter(answer__question__quiz=quiz, answer__is_correct=True).count()
    percentage_is_above_70 = (obtained_marks / total_marks) * 100 > 70.0

    TakenQuiz.objects.create(
      student=student,
      quiz=quiz,
      obtained_marks=obtained_marks
    )

    if percentage_is_above_70:
      response = {
        'message': f'Congractulations! You have got such an amazing marks {obtained_marks} out of {total_marks}'
      }
    else:
      response = {
        'message': f'Fair! You have to work hard {obtained_marks} out of {total_marks}'
      }

    return self.render_json_response(response)