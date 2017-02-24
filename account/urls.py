from django.conf.urls import url
import account.views as views

urlpatterns = [
    url(r'^$', views.account, name='account'),
]