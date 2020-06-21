from django.urls import path
from .views import search,downloaded,search_more

app_name="backend"

urlpatterns = [
  path("search/",search,name="search"),
  path("search_more/",search_more,name="search_more"),
  path("downloaded/",downloaded,name="downloaded"),
]