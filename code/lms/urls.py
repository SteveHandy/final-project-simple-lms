from django.contrib import admin
from django.urls import include, path
from api import api

urlpatterns = [
    path("admin/", admin.site.urls),
    path("silk/", include("silk.urls", namespace="silk")),
    path("api/", api.urls),
    path("", include("courses.urls")),
]