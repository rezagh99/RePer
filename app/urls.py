from django.urls import path, include

from app import views

urlpatterns = [
    path('', views.dashboard, name="home"),
    path('service/', views.result, name='service'),
    path('contact/', views.contact, name='contact'),
]
