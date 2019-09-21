from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [
    #path('', views.home, name='takatarecovery-home'),
    path('', views.home, name='takatarecovery-home'),
    path('makemodel/', views.makemodel, name='takatarecovery-makemodel'),
    path('aboutus/', views.aboutus, name='takatarecovery-aboutus'),
    path('privacy/', views.privacy, name='takatarecovery-privacy'),
    path('contact/', views.contact, name='takatarecovery-contact'),
    path('index-result/', views.details, name='takatarecovery-details'),
    path('make-model/', views.makeModelCheck, name='takatarecovery-makeModelCheck')
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)