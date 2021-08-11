
"""
DELETES THE PROGRESS OF PREVIOUSLY ATTEMPTED QUIZ
"""

def remove_previous_progress(student, quiz):
    attempted_quiz = student.taken_quizzes.get(student=student, quiz=quiz)
    attempted_quiz.delete()

    [quiz_answer.delete() for quiz_answer in student.quiz_answers.filter(answer__question__quiz=quiz, student=student)]