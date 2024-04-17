from django.urls import path
from . import views


urlpatterns=[

    path('yayinlar', views.list_yayinlar, name='yayinlar_listesi'),
    path('search', views.search_view, name='search_view'),
    path('search_and_scrape', views.search_and_scrape, name='search_and_scrape'),
    path('search_and_fetch/', views.search_and_fetch, name='search_and_fetch'),
    path('download-pdf/<path:pdf_url>/', views.download_pdf, name='download_pdf'),
    path('filter_yayinlar',views.filter_yayinlar,name='filter_yayinlar'),
    path('filtrele',views.list_yayinlar,name='list_yayinlar')
 
]