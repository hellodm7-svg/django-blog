from django.urls import path
from . import views

app_name = 'board'

urlpatterns = [
    path('',                                    views.post_list,      name='post_list'),
    path('new/',                                views.post_create,    name='post_create'),
    path('<int:pk>/',                           views.post_detail,    name='post_detail'),
    path('<int:pk>/edit/',                      views.post_edit,      name='post_edit'),
    path('<int:pk>/delete/',                    views.post_delete,    name='post_delete'),
    path('<int:pk>/comment/',                   views.comment_create, name='comment_create'),
    path('<int:pk>/comment/<int:comment_pk>/edit/',   views.comment_edit,   name='comment_edit'),
    path('<int:pk>/comment/<int:comment_pk>/delete/', views.comment_delete, name='comment_delete'),
]
