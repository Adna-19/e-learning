from django.urls import path
from django.views.decorators.cache import cache_page
from .views import (
  course_views, 
  module_views, 
  content_views, 
  student_views,
  notification_views,
  blog_views
)

# PATTERNS FOR COURSE_VIEWS
urlpatterns = [
  path(
    'cms/home/', 
    course_views.CMSHomePageView.as_view(), 
    name='cms_home_page'
  ),
  path(
    'mine/', 
    course_views.ManageCourseListView.as_view(), 
    name='manage_course_list'
  ),
  path(
    'create/', 
    course_views.CourseCreateView.as_view(), 
    name='create_course'
  ),
  path(
    '<slug:slug>/edit/', 
    course_views.CourseUpdateView.as_view(), 
    name='update_course'
  ),
  path(
    'trash/list/',
    course_views.CMSTrashListView.as_view(),
    name='cms_courses_trash'
  ),
  path(
    '<slug:course_slug>/trash/<str:action>/',
    course_views.CourseTrashedUntrashedView.as_view(),
    name='trash_untrash_course'
  ),
  path(
    'trash/empty/', 
    course_views.TrashEmptyingView.as_view(), 
    name='empty_courses_trash'
  ),
]

# PATTERNS FOR MODULE_VIEWS
urlpatterns += [
  path(
    '<slug:slug>/modules/', 
    module_views.ModulesListView.as_view(), 
    name='modules_list'
  ),
  path(
    '<slug:slug>/manage-modules/', 
    module_views.ModulesCreateUpdateView.as_view(), 
    name='manage_course_modules'
  ),
  path(
    '<slug:slug>/delete-module/', 
    module_views.ModuleDeleteView.as_view(), 
    name='delete_module'
  ),
  path('module/order', module_views.ModuleOrderView.as_view(), name='order_module'),
]

# PATTERNS FOR CONTENT_VIEWS
urlpatterns += [
  path(
    'module/<slug:slug>/contents/', 
    content_views.ModuleContentListView.as_view(), 
    name='content_list'
  ),
  path(
    'module/<slug:slug>/contents/<model_name>/create/', 
    content_views.ContentCreateUpdateView.as_view(), 
    name='content_create'
  ),
  path(
    'module/<slug:slug>/contents/<model_name>/<int:id>/update/', 
    content_views.ContentCreateUpdateView.as_view(), 
    name='content_update'
  ),
  path(
    'module/<slug:slug>/content/<model_name>/<int:id>/delete/', 
    content_views.ContentDeleteView.as_view(), 
    name='content_delete'
  ),
  path('module/content/order/', content_views.ContentOrderView.as_view(), name='order_content')
]

# CMS BLOG VIEWS PATTERNS 

urlpatterns += [
  path(
    'cms/blog/',
    blog_views.CMSPostListView.as_view(),
    name='cms_blog'
  ),
]


# SITE PUBLIC USER PATTERNS 

urlpatterns += [

  path('home/', student_views.HomePageView.as_view(), name='home'),
  path('about/', student_views.AboutPageView.as_view(), name='about'),
  path('contact/', student_views.ContactPageView.as_view(), name='contact'),
  path(
    'courses/free-courses/', 
    student_views.StudentCoursesListView.as_view(), 
    name='free_courses'
  ),
  path(
    'courses/<int:paid>/paid-courses/', 
    student_views.StudentCoursesListView.as_view(), 
    name='paid_courses'
  ),

  path(
    '<slug:course_slug>/review/',
    student_views.StudentCourseReviewAndRatingView.as_view(),
    name='course_review'),

  path(
    'teachers/list/',
    student_views.TeachersListView.as_view(),
    name='teachers_list'
  ),

  path(
    'teachers/<int:pk>/details/',
    student_views.TeacherDetailView.as_view(),
    name='teachers_detail'
  ),

  # path('<slug:slug>/courses/', student_views.StudentCoursesListView.as_view(), name='course_list_by_subject'),
  
  path(
    '<slug:slug>/details/', 
    cache_page(60*15)(student_views.StudentCourseDetailView.as_view()), 
    name='course_details'
  ),

  path(
    'module/<slug:slug>/details/', 
    cache_page(60*15)(student_views.StudentCourseModuleDetailView.as_view()), 
    name='course_module_details'
  ),
  path(
    '<slug:slug>/<int:id>/enroll/', 
    student_views.StudentCourseEnrollmentView.as_view(), 
    name='course_enroll'
  ),
  path(
    '<slug:slug>/<int:id>/disenroll/', 
    student_views.StudentCourseDisenrollmentView.as_view(), 
    name='course_disenroll'
  ),
  path(
    'student/classroom/', 
    student_views.ClassroomDashboardView.as_view(), 
    name='student_dashboard'
  ),  

  path(
    'student/classroom/course/<slug:course_slug>/details/',
    student_views.ClassroomCourseDetailView.as_view(),
    name='classroom_course_details'
  ),

  path(
    'student/classroom/course/<slug:course_slug>/module/<slug:module_slug>/contents/',
    student_views.ClassroomModuleContentsView.as_view(),
    name='classroom_module_contents'
  ),

  path(
    'student/classroom/course/<slug:course_slug>/module/<slug:module_slug>/contents/<int:next_content>/',
    student_views.ClassroomModuleContentsView.as_view(),
    name='classroom_module_contents_next'
  ),

  path(
    'student/classroom/acheivements/',
    student_views.ClassroomAcheivementsView.as_view(),
    name='classroom_achievments'
  ),

  path(
    'student/classroom/course/<slug:course_slug>/generate/certificate/',
    student_views.completeCourseAndGenerateCertificate.as_view(),
    name='generate_course_certificate'
  ),

  path(
    'student/classroom/profile/settings/',
    student_views.ProfileSettingView.as_view(),
    name='profile_settings'
  ),

  path('cart/items/', student_views.ShowCartItemsView.as_view(), name='show_cart'),
  path(
    '<slug:slug>/add-to-cart/', 
    student_views.AddCourseToCartView.as_view(), 
    name='add_to_cart'
  ),
  path(
    '<slug:slug>/remove-from-cart/', 
    student_views.RemoveItemFromCartView.as_view(), 
    name='remove_from_cart'
  ),
]

# PAYMENT URL PATTERNS 

urlpatterns += [
  path(
    'process-payment/<amount>/', 
    student_views.PayPalPaymentView.as_view(), 
    name='payment_process'
  ),

  path(
    'paypal-return/', 
    student_views.PayPalPaymentSuccessView.as_view(), 
    name='paypal-return'
  ),
  
  path(
    'paypal-cancel/', 
    student_views.PayPalPaymentRejectView.as_view(), 
    name='paypal-cancel'
  ),
]

# NOTIFICATION URL PATTERNS 
urlpatterns += [
  path(
    'cms/notifications/', 
    notification_views.NotificationListView.as_view(), 
    name='cms_notifications'
  ),
  path(
    'cms/notification/<int:pk>/',
    notification_views.NotificationDetailView.as_view(),
    name='notification_details'
  ),
]