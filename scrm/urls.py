from django.conf import settings
from django.conf.urls import include, url
from django.conf.urls.static import static
from django.contrib import admin 

from extracao import views


urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^$', views.home, name='scrm_index'),
    url(r'^extracao/', include("extracao.urls")),
    url(r'^email/$', views.email, name='email'),
    url(r'^thanks/$', views.thanks, name='thanks'),
    url(r'^', include("extracao.urls")),  
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.ARQUIVOS_URL, document_root=settings.ARQUIVOS_ROOT)
