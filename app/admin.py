from django.contrib import admin
from .models import Question, Answer, QuestionLike, AnswerLike, Tag, Profile


class QuestionAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'author', 'creating_time', 'editing_time')


class ProfileAdmin(admin.ModelAdmin):
    list_display = ('id', 'user')


class TagAdmin(admin.ModelAdmin):
    list_display = ('title',)


class AnswerAdmin(admin.ModelAdmin):
    list_display = ('id', 'description', 'author', 'creating_time', 'editing_time')


class AnswerLikeAdmin(admin.ModelAdmin):
    list_display = ('id', 'type', 'answer')


class QuestionLikeAdmin(admin.ModelAdmin):
    list_display = ('id', 'type', 'question')


admin.site.register(Question, QuestionAdmin)
admin.site.register(Profile, ProfileAdmin)
admin.site.register(Tag, TagAdmin)
admin.site.register(Answer, AnswerAdmin)
admin.site.register(AnswerLike, AnswerLikeAdmin)
admin.site.register(QuestionLike, QuestionLikeAdmin)