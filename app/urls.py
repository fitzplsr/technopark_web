from django.urls import path
from app import views

urlpatterns = [
    path('', views.index, name='index'),
    path('hot/', views.hot_questions, name='hot_questions'),
    path('best/', views.best_questions, name='best_questions'),
    path('new/', views.new_questions, name='new_questions'),
    path('tag/<str:tag>', views.tag_questions, name='tag_questions'),
    path('question/<int:question_id>', views.question, name='question')
]