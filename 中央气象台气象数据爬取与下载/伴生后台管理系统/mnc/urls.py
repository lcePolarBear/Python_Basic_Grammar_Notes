from django.urls import path, re_path
from mnc import views

urlpatterns = [
    re_path('^index/$', views.mnc, name="mnc"),
    re_path('^Urllist_func/$', views.Urllist_func, name="Urllist_func"),
    re_path('^Urllist_create/$', views.Urllist_create, name="Urllist_create"),
    re_path('^Taglist_func/', views.Taglist_func, name="Taglist_func"),
    re_path('Taglist_create/', views.Taglist_create, name="Taglist_create")
]
