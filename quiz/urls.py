from django.urls import path
from .views import instructor_views, student_views

# Teacher views patterns
urlpatterns = [
  path(
  	'teachers/all/quizzes/', 
  	instructor_views.TeacherQuizHomeView.as_view(), 
  	name='quizzes_list'),
  path(
  	'teachers/<slug:course_slug>/quizzes/', 
  	instructor_views.TeacherQuizHomeView.as_view(), 
  	name='quizzes_by_specific_course'),
  path(
  	'teachers/quiz/<int:pk>/details/', 
  	instructor_views.TeacherQuizDetailView.as_view(), 
  	name='quiz_cms_details'),
  path(
  	'quiz/<slug:course_slug>/create/', 
  	instructor_views.QuizCreateUpdateView.as_view(), 
  	name='create_quiz'),
  path(
  	'quiz/<slug:course_slug>/<int:id>/update/', 
  	instructor_views.QuizCreateUpdateView.as_view(), 
  	name='update_quiz'),
  path(
  	'quiz/<int:id>/delete/', 
  	instructor_views.QuizDeleteView.as_view(), 
  	name='delete_quiz'),
  path(
  	'quiz/question/<int:pk>/delete/', 
  	instructor_views.QuestionDeleteView.as_view(), 
  	name='delete_question'),
  path(
  	'quiz/<int:pk>/question/create/', 
  	instructor_views.QuestionCreateUpdateView.as_view(), 
  	name='create_question'),
  path(
  	'<int:pk>/question/<int:question_id>/update/', 
  	instructor_views.QuestionCreateUpdateView.as_view(), 
  	name='update_question'),
  path(
  	'questions/order/', 
  	instructor_views.OrderQuestion.as_view(), 
  	name='order_questions'),
]

# STUDENTS LOGIC PATTERNS

urlpatterns += [
  path(
  	'students/home/', 
  	student_views.StudentHomeView.as_view(), 
  	name='students_dashboard'),
  path(
  	'students/quiz/<int:pk>/details/', 
  	student_views.StudentQuizDetailView.as_view(), 
  	name='quiz_details'),
  path(
  	'students/quiz/<int:quiz_id>/attempt/', 
  	student_views.StudentQuizAttemptView.as_view(), 
  	name='attempt_quiz'),
]