from django.conf.urls import url
import quiz.views as views

urlpatterns = [
    url(r'^$', views.question, name='question'),
    url(r'^new/multiplechoice', views.newMultiplechoice, name='question'),
    url(r'^new/trueorfalse', views.newTrueorfalse, name='question'),
    url(r'^new/textanswer', views.newTextanswer, name='question'),

]
