from django.conf import settings
from django.contrib.sites.models import Site


def main_context(request):
    is_suspended = False
    if not request.session.exists(request.session.session_key):
        request.session.create()

    domain = request.META.get("HTTP_HOST", "")
    site_name = "Ajoneedienen"
    logo_url = "/static/main/images/logo.png"
    favicon_url = "/static/main/images/logo_mini.svg"

    if not Site.objects.filter(pk=settings.SITE_ID).exists():
        new_site = Site(pk=settings.SITE_ID, domain=domain, name=site_name)
        new_site.save()

    if request.user.is_authenticated:
        usertype = "Administator" if request.user.is_superuser else "Restaurant"
    else:
        usertype = "Guest"
    return {
        "site_name": site_name,
        "logo_url": logo_url,
        "favicon_url": favicon_url,
        "usertype": usertype,
        "domain": "https://www.ajoneedienen.com",
        "is_suspended": is_suspended,
    }
