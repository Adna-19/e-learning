from django.contrib import admin
from .models import *

admin.site.register(StudentProfile)
admin.site.register(InstructorProfile)
admin.site.register(User)