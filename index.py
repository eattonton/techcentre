# -*- coding: utf-8 -*-
import os, sys
# sys.path.append("WeldStaffPy")
import json
from django.http import HttpResponse, HttpResponseBadRequest
from django.conf.urls import url
from django.core.wsgi import get_wsgi_application
from django.conf import settings

BASE_DIR = os.path.dirname(__file__)

settings.configure(
    DEBUG=True,
    SECRET_KEY='thisisthe',
    ROOT_URLCONF=__name__,
    ALLOWED_HOSTS=['*'],
    MIDDLEWARE_CLASSES=(
        'django.middleware.common.CommonMiddleware',
        'django.middleware.clickjacking.XFrameOptionsMiddleware',
    ),
    INSTALL_APPS=(
        'django.contrib.staticfiles',
    ),
    TEMPLATES=(
        {
            'BACKEND': 'django.template.backends.django.DjangoTemplates',
            'DIRS': (os.path.join(BASE_DIR, 'templates'),),
        },
    ),
    STATICFILES_DIRS=(
        os.path.join(BASE_DIR, 'static'),
    ),
    STATIC_URL='/static/',
    USE_I18N=False,
    SITE_PAGES_DIRECTORY=os.path.join(BASE_DIR, 'static'),
)

from django.shortcuts import render, render_to_response
from django.views.static import serve

# user defined
import tcpy.main
from techwebapp.src import _parttern

urlpatterns = (
    url(r'^$', serve, {'document_root': 'static', 'path': 'index.html', 'show_indexes': True}),
    url(r'^templates/(?P<path>.*)', serve, {'document_root': 'templates', 'show_indexes': True}),
    url(r'^tc/(.*)/(.*)', tcpy.main.html),
    url(r'^dictionary/(.*)', _parttern.dictionary),
    url(r'^works/(.*)', _parttern.works),
    url(r'^(?P<path>.*)$', serve, {'document_root': 'static', 'show_indexes': True}),
)

# application = get_wsgi_application()

if __name__ == '__main__':
    from django.core.management import execute_from_command_line

    execute_from_command_line(sys.argv)
