__author__ = 'pietrelli'

from django.conf.urls import url
from django.contrib.auth.decorators import login_required
from django.conf.urls import handler404, handler500

from . import views
cache = {}
urlpatterns = [
    ## Project page
    url(r'^(?P<project_name>\w+)/$', views.project_homepage, name='index'),
    #url(r'^test/$', views.IndexView.as_view(), name='index'),
    #url(r'^login/$', views.user_login, name='user_login'),
    #url(r'^logout/$', views.user_logout, name='user_logout'),

    ## Search page
    url(r'^(?P<project_name>\w+)/search/$', views.search, name='search'),
    # Not found page
    url(r'^(?P<project_name>\w+)/not_found/(?P<q>\w+)$', views.not_found, name='not_found'),

    ## Results
    # Gene page
    url(r'^(?P<project_name>\w+)/gene/(?P<gene_ensgene>ENSG[0-9]+)/$', views.display_gene_results, name='gene_list'),
    # Region page
    url(r'^(?P<project_name>\w+)/region/(?P<region>[0-9XY]{1,2}-[0-9]+-[0-9]+)/$', views.display_region_results, name='region'),
    # Variant page
    url(r'^(?P<project_name>\w+)/variant/(?P<variant>[0-9XY]{1,2}-[0-9]+-[0-9]+-[Aa,Tt,Gg,Cc]+-[Aa,Tt,Gg,Cc]+)/$', views.display_variant_results, name='variant'),
    url(r'^(?P<project_name>\w+)/variant/(?P<variant>[0-9XY]{1,2}-[0-9]+-[0-9]+-[Aa,Tt,Gg,Cc]+-[Aa,Tt,Gg,Cc]+)/get_exac_data/$', views.get_exac_data, name='exac'),
    url(r'^(?P<project_name>\w+)/variant/(?P<variant>[0-9XY]{1,2}-[0-9]+-[0-9]+-[Aa,Tt,Gg,Cc]+-[Aa,Tt,Gg,Cc]+)/get_esp_data/$', views.get_esp_data, name='esp'),
    url(r'^(?P<project_name>\w+)/variant/(?P<variant>[0-9XY]{1,2}-[0-9]+-[0-9]+-[Aa,Tt,Gg,Cc]+-[Aa,Tt,Gg,Cc]+)/get_1000g_data/$', views.get_1000g_data, name='1000g'),

    ## Settings
    url(r'^(?P<project_name>\w+)/settings/$', views.settings, name='settings'),
    url(r'^(?P<project_name>\w+)/settings/get_col_list/$', views.get_col_list, name='get_col_list'),
    url(r'^(?P<project_name>\w+)/settings/save_preferences/$', views.save_preferences, name='save_preferences'),

    ## Summary statistics
    url(r'^(?P<project_name>\w+)/summary_statistics/$', views.summary_statistics, name='summary_statistics'),
    url(r'^(?P<project_name>\w+)/summary_statistics/get_qual_vcf/$', views.get_qual_vcf, {'cache': cache} ),
    url(r'^(?P<project_name>\w+)/summary_statistics/get_mean_variations/$', views.get_mean_variations, {'cache': cache} ),
    url(r'^(?P<project_name>\w+)/summary_statistics/get_exonictype_variations/$', views.get_exonictype_variations, {'cache': cache} ),
    url(r'^(?P<project_name>\w+)/summary_statistics/get_biotype_variations/$', views.get_biotype_variations, {'cache': cache} ),
    url(r'^(?P<project_name>\w+)/summary_statistics/get_chr_variations/$', views.get_chr_variations, {'cache': cache} ),
    url(r'^(?P<project_name>\w+)/summary_statistics/get_top_genes/$', views.get_top_genes, {'cache': cache} ),
    #url(r'^search_json/$', views.VcfToJson, name='search_json'),
    #url(r'^search.html$', views.SearchView.as_view(), name='search')
    #url(r'^(?P<pk>[0-9]+)/$', views.DetailView.as_view(), name='detail'),
    #url(r'^(?P<pk>[0-9]+)/results/$', views.ResultsView.as_view(), name='results'),
    #url(r'^(?P<question_id>[0-9]+)/vote/$', views.vote, name='vote'),

    ## Other VCF (Non-human or not annotated)
    ## Project page
    url(r'^other/(?P<project_name>\w+)/$', views.project_homepage, name='index'),
    ## Search page
    url(r'^other/(?P<project_name>\w+)/search/$', views.search, name='search'),
    # Not found page
    url(r'^other/(?P<project_name>\w+)/not_found/(?P<q>\w+)$', views.not_found, name='not_found'),

    ## Results
    # Region page
    url(r'^other/(?P<project_name>\w+)/region/(?P<region>[A-z0-9]+-[0-9]+-[0-9]+)/$', views.display_region_results, name='region'),
    # Variant page
    url(r'^other/(?P<project_name>\w+)/variant/(?P<variant>[A-z0-9]+-[0-9]+-[0-9]+-[Aa,Tt,Gg,Cc]+-[Aa,Tt,Gg,Cc]+)/$', views.display_variant_results, name='variant'),

    ## Settings
    url(r'^other/(?P<project_name>\w+)/settings/$', views.settings, name='settings'),
    url(r'^other/(?P<project_name>\w+)/settings/get_col_list/$', views.get_col_list, name='get_col_list'),
    url(r'^other/(?P<project_name>\w+)/settings/save_preferences/$', views.save_preferences, name='save_preferences'),

    ## Summary statistics
    url(r'^other/(?P<project_name>\w+)/summary_statistics/$', views.summary_statistics, name='summary_statistics'),
    url(r'^other/(?P<project_name>\w+)/summary_statistics/get_qual_vcf/$', views.get_qual_vcf, {'cache': cache} ),
    url(r'^other/(?P<project_name>\w+)/summary_statistics/get_mean_variations/$', views.get_mean_variations, {'cache': cache} ),
    url(r'^(?P<project_name>\w+)/summary_statistics/get_chr_variations/$', views.get_chr_variations, {'cache': cache} )

]


handler404 = views.error404
handler500 = views.error500