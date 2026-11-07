from django.urls import path

from . import views

urlpatterns = [
    path("robots.txt", views.robots_txt, name="robots_txt"),
    path("", views.home, name="accueil"),
    path("maison/<slug:slug>/", views.house_detail, name="maison"),
    path("depenser/", views.spend_points, name="depenser"),
    path("ajouter/", views.add_points, name="ajouter"),
]
