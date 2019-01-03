"""
Definition of urls for CatLaser.
"""

from datetime import datetime
from django.urls import path
from django.conf.urls import url
from django.contrib.auth import views as auth_views

import app.forms
import app.views as views
import app.ajax as ajax

# enables the admin:
from django.contrib import admin

admin.autodiscover()

urlpatterns = [
    # ajax
    path(r'^ajax/change_active/$', ajax.change_active, name='change_active'),

    # Examples:
    path('admin', admin.site.urls),
    url(r'^$', views.home, name='home'),
    url(r'^contact$', views.contact, name='contact'),
    url(r'^about$', views.about, name='about'),
    url( r'^login/$',auth_views.LoginView.as_view(template_name="app/login.html"), name="login"),
    url( r'^logout$',auth_views.LogoutView.as_view(template_name="app/index.html"), name="logout"),
]

#one_time_startup()