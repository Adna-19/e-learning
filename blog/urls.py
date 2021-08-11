from django.urls import path
from . import views 

urlpatterns = [
	path('list/', views.PostListView.as_view(), name='posts_list'),
	path('<int:pk>/details/', views.PostDetailView.as_view(), name='post_details'),
	path('post/create/', views.ArticleCreateView.as_view(), name='create_post'),
	path('post/<slug:post_slug>/update/', views.ArticleUpdateView.as_view(), name='update_post'),
	path('post/<slug:post_slug>/<str:action>/', views.TrashUnTrashArticle.as_view(), name='trash_or_restore'),
	path('trash/list/', views.TrashListView.as_view(), name='open_trash'),
	path('trash/empty/', views.EmptyBlogTrashView.as_view(), name='empty_blog_trash'),
	path('<slug:post_slug>/add-comment/', views.PostCommentView.as_view(), name='add_comment'),
	path('comment/<int:comment_id>/reply/', views.CommentReplyView.as_view(), name='add_reply'),
	path('comment/<int:comment_id>/delete/', views.CommentDeleteView.as_view(), name='delete_comment'),
	path('comment/<int:comment_id>/reply/<int:reply_id>/delete/', views.CommentReplyDeleteView.as_view(), name='delete_reply'),
]