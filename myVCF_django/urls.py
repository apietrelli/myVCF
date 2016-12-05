"""epidemic URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.8/topics/http/urls/
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
from django.conf.urls import include, url
from django.conf import settings
from myVCF_django import views as myVCF_view


urlpatterns = [
    url(r'^$', myVCF_view.main_page),
    url(r'^delete_db/$', myVCF_view.delete_db),
    url(r'^upload/$', myVCF_view.upload_project),
    url(r'^upload/preprocessing_vcf/$', myVCF_view.preprocessing_vcf),
    url(r'^upload/select_vcf/$', myVCF_view.select_vcf),
    url(r'^upload/submit_vcf/$', myVCF_view.submit_vcf),
    url(r'^upload/check_project_name/$', myVCF_view.check_project_name),

    url(r'^vcfdb/', include('vcfdb.urls', namespace="vcfdb")),
    #url(r'^vcfdb_vep/', include('vcfdb_vep.urls', namespace="vcfdb_vep")),

    url(r'^static/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.STATIC_ROOT}),
]
