from django.conf.urls import url, include
from django.urls import path
from forms import views
from members import view

urlpatterns = [
    url(r'^$', views.form_view, name='form_view'),
    url(r'^ajax/$', views.lat_ajax, name='lat_ajax'),
    path('formsubmit/', views.form_submit, name='form_submit'),
    url(r'^activate/(?P<uidb64>[0-9A-Za-z_\-]+)/$',
        views.activate, name='activate'),
    url(r'^director/activate/(?P<uidb64>[0-9A-Za-z_\-]+)/$',
        views.director_activate, name='director_activate'),
    url(r'^member/director/activate/(?P<uidb64>[0-9A-Za-z_\-]+)/$',
        view.member_activate, name='member_activate'),
    url(r'^cancel/director/activate/(?P<uidb64>[0-9A-Za-z_\-]+)/$',
        views.cancel_booking, name='cancel_booking'),
]
