"""
edx_exams URL Configuration.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Add an import:  from blog import urls as blog_urls
    2. Add a URL to urlpatterns:  url(r'^blog/', include(blog_urls))
"""

import os

from auth_backends.urls import oauth2_urlpatterns
from django.conf import settings
from django.conf.urls import include, url
from django.contrib import admin
from edx_api_doc_tools import make_api_info, make_docs_urls

from edx_exams.apps.api import urls as api_urls
from edx_exams.apps.core import views as core_views
from edx_exams.apps.lti import urls as lti_urls

admin.autodiscover()

urlpatterns = oauth2_urlpatterns + [
    url(r'^admin/', admin.site.urls),
    url(r'^api/', include(api_urls)),
    url(r'^auto_auth/$', core_views.AutoAuth.as_view(), name='auto_auth'),
    url(r'', include('csrf.urls')),  # Include csrf urls from edx-drf-extensions
    url(r'^health/$', core_views.Health.as_view(), name='health'),
    url(r'^lti/', include(lti_urls)),
]

if settings.DEBUG and os.environ.get('ENABLE_DJANGO_TOOLBAR', False):  # pragma: no cover
    # Disable pylint import error because we don't install django-debug-toolbar
    # for CI build
    import debug_toolbar  # pylint: disable=import-error
    urlpatterns.append(url(r'^__debug__/', include(debug_toolbar.urls)))

api_info = make_api_info(
    title="edX Exams API",
    version="v0",
    description="A REST API for interacting with the edX exams service."
)

urlpatterns += make_docs_urls(
    api_info,
    api_url_patterns=[url(r'^health/$', core_views.Health.as_view(), name='health'), url(r'^api/', include(api_urls))]
)
