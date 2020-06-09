from django.urls import path
from rest_framework.urlpatterns import format_suffix_patterns
from .views import visited_links_handle, visited_domains_handle

urlpatterns = {
    path('visited_links', visited_links_handle, name="visited_links"),
    path('visited_domains', visited_domains_handle, name="visited_domains")
}
urlpatterns = format_suffix_patterns(urlpatterns)