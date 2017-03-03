from django.conf.urls import url
import authentication.views as views

urlpatterns = [
    url(r'^login/', views.login, name='login'),
    url(r'^logout/', views.logout, name='logout'),
    url(r'^$', views.register, name='register'),
]
