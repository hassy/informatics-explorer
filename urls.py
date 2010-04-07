import settings
from django.conf.urls.defaults import *

# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

urlpatterns = patterns('',
    url(r'^$', 'views.home'),
    url(r"init_json$", "views.init_json"),
    url(r"query$", "views.app_query"),
    url(r"person/(?P<person_id>.+)$", "views.person_details"),
    url(r"buddies$", "views.buddies_index"),
    url(r"buddies/(?P<person_id>.+)", "views.person_buddies"),
    url(r"static_graph", "views.static_graph"),

    url(r'^static/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.MEDIA_ROOT, "show_indexes": True}),
)