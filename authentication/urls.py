from django.conf.urls import url
import authentication.views as views

urlpatterns = [
    url(r'^$', views.login, name='login'),
]