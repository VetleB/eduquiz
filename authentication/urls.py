from django.conf.urls import url
import authentication.views as views

urlpatterns = [
    url(r'^login/', views.login, name='login'),
    url(r'^logout/', views.logout, name='logout'),
    url(r'^register/', views.register, name='register'),
    url(r'^account/', views.account, name='account'),
    url(r'^change_pswd/$', views.change_pswd, name='change_pswd'),
    url(r'^change_name/$', views.change_name, name='change_name'),
]
