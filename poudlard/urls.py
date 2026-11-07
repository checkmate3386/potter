from django.conf import settings
from django.contrib import admin
from django.urls import include, path

admin.site.site_header = "Gestion des points des maisons"
admin.site.site_title = "Administration de Poudlard"
admin.site.index_title = "Administration"

urlpatterns = [
    path(settings.ADMIN_URL, admin.site.urls),
    path("", include("points.urls")),
]
