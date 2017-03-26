from django.conf.urls import url
import quiz.views as views

urlpatterns = [
    url(r'^$', views.question, name='question'),
    url(r'^select-topics/', views.selectTopic, name='selectTopic'),
    url(r'^new/multiplechoice', views.newMultiplechoiceQuestion, name='newMultiplechoiceQuestion'),
    url(r'^new/truefalse', views.newTrueFalseQuestion, name='newTrueFalseQuestion'),
    url(r'^new/text', views.newTextQuestion, name='newTextQuestion'),
    url(r'^new/', views.newQuestion, name='newQuestion'),
    url(r'^report/', views.report, name='report'),
    url(r'^viewreports/$', views.viewReports, name='viewReport'),
    url(r'^viewreports/handlereport/(?P<question_id>[0-9]+)/$', views.handleReport, name='handleReport'),
]
