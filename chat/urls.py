from django.urls import URLPattern, URLResolver, path
from typing import List

from . import views

urlpatterns: List[URLPattern | URLResolver] = [path("", views.index, name="index")]
