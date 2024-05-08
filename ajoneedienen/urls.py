from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from django.views.generic import TemplateView
from web.views import handler404

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("web.urls", namespace="web")),
    path("", include("main.urls", namespace="main")),
    path("accounts/", include("registration.backends.simple.urls")),
    path("sitemap.xml", TemplateView.as_view(template_name="sitemap.xml", content_type="text/xml")),
    path("robots.txt", TemplateView.as_view(template_name="robots.txt", content_type="text/plain")),
    *static(settings.STATIC_URL, document_root=settings.STATIC_ROOT),
    *static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT),
]

handler404 = handler404

admin.site.site_header = "Ajoneedienen Administration"
admin.site.site_title = "Ajoneedienen Admin Portal"
admin.site.index_title = "Welcome to Ajoneedienen Admin Portal"
