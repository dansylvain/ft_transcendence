from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="user_index"),
    path("delete-profile/", views.delete_profile, name="delete_profile"),
]
