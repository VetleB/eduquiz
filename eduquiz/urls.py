from django.conf.urls import include, url
from django.contrib import admin
import eduquiz.views as views

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^$', views.index, name='index'),
    url(r'^quiz/', include('quiz.urls')),
]
