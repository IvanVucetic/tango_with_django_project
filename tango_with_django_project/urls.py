from django.conf import settings #allows access to variables in project's settings.py file
from django.conf.urls import patterns, include, url
from django.contrib import admin

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'tango_with_django_project.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),

    url(r'^admin/', include(admin.site.urls)),
    url(r'^rango/', include('rango.urls')),
)

if settings.DEBUG: # if project is in debug mode, additional url pattern is added to the urlpatterns tuple
	urlpatterns += patterns(
		'django.views.static',	#handles dispatching of uploaded media
		(r'^media/(?P<path>.*)', # for any file request with url starting with 'media', passed to django.views.static view
		'serve',
		{'document_root': settings.MEDIA_ROOT}),)