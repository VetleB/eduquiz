from django.conf.urls import url
import quiz.views as views

urlpatterns = [
    url(r'^$', views.question, name='question'),
    url(r'^select-topics/', views.select_topic, name='selectTopic'),
    url(r'^new/multiplechoice', views.new_multiple_choice_question, name='newMultiplechoiceQuestion'),
    url(r'^new/truefalse', views.new_true_false_question, name='newTrueFalseQuestion'),
    url(r'^new/text', views.new_text_question, name='newTextQuestion'),
    url(r'^new/', views.new_question, name='newQuestion'),
    url(r'^report/', views.report, name='report'),
    url(r'^viewreports/$', views.view_reports, name='viewReport'),
    url(r'^viewreports/handlereport/(?P<question_id>[0-9]+)/$', views.handle_report, name='handleReport'),
    url(r'^viewreports/deletequestion/(?P<question_id>[0-9]+)/$', views.delete_report, name='deleteReport'),
    url(r'^stats/(?P<subject_id>[0-9]+)', views.stats, name='stats'),
    url(r'^stats/', views.stats_default, name='statsDefault'),
]
