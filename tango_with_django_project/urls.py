from django.conf import settings #allows access to variables in project's settings.py file
from django.conf.urls import patterns, include, url
from django.contrib import admin
from registration.backends.simple.views import RegistrationView

# Create a new class that redirects the user to the index page, if successful at logging
class MyRegistrationView(RegistrationView):
    def get_success_url(self, request, user):
        return '/rango/'

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'tango_with_django_project.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),

    url(r'^admin/', include(admin.site.urls)),
    url(r'^rango/', include('rango.urls')),
        #Add in this url pattern to override the default pattern in accounts.
    url(r'^accounts/register/$', MyRegistrationView.as_view(), name='registration_register'),
    url(r'^accounts/', include('registration.backends.simple.urls')),
)

if settings.DEBUG: # if project is in debug mode, additional url pattern is added to the urlpatterns tuple
	urlpatterns += patterns(
		'django.views.static',	#handles dispatching of uploaded media
		(r'^media/(?P<path>.*)', # for any file request with url starting with 'media', passed to django.views.static view
		'serve',
		{'document_root': settings.MEDIA_ROOT}),)