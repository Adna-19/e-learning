from django.contrib import admin
from .models import *

@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):
  list_display = ['name', 'code']

class ModuleInline(admin.StackedInline):
  model = Module

@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
  list_display = ['title', 'subject', 'instructor', 'payment_status', 'date_created', 'date_updated']

  list_filter = ['subject', 'date_created', 'payment_status']
  inlines = [ModuleInline]

admin.site.register(Content)

admin.site.register(Text)
admin.site.register(Video)
admin.site.register(Image)
admin.site.register(File)

admin.site.register(Order)
admin.site.register(OrderItem)
admin.site.register(Review)

admin.site.register(Acheivement)
