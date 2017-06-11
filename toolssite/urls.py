"""toolssite URL Configuration
"""
from django.conf.urls import include, url
from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.sitemaps.views import sitemap

from tool.views import tool, worklogs, calendar, dictionary, flashcards, users_list, profile_view, update_profile, card_order, log_in, log_out
from tool.sitemaps import StaticViewSitemap

sitemaps = {
    'static': StaticViewSitemap,
}


urlpatterns = [
    url(r'^$', tool, name='main', kwargs={'slug': 'jira-logs'}),
    url(r'^ajax$', tool, name='ajax_main', kwargs={'slug': 'jira-logs'}),
    url(r'^tool/(?P<slug>[^/]+)$', tool, name='tool'),
    url(r'^ajax/tool/(?P<slug>[^/]+)$', tool, name='ajax_tool'),
    url(r'^calendar$', calendar, name='calendar'),
    url(r'^ajax/calendar$', calendar, name='ajax_calendar'),
    url(r'^user/(?P<username>[^/]+)/calendar$', calendar, name='user_calendar'),
    url(r'^ajax/user/(?P<username>[^/]+)/calendar$', calendar, name='ajax_user_calendar'),
    url(r'^dictionary$', dictionary, name='dictionary'),
    url(r'^ajax/dictionary$', dictionary, name='ajax_dictionary'),
    url(r'^user/(?P<username>[^/]+)/dictionary$', dictionary, name='user_dictionary'),
    url(r'^ajax/user/(?P<username>[^/]+)/dictionary$', dictionary, name='ajax_user_dictionary'),
    url(r'^flashcards$', flashcards, name='flashcards'),
    url(r'^ajax/flashcards$', flashcards, name='ajax_flashcards'),
    url(r'^user/(?P<username>[^/]+)/flashcards$', flashcards, name='user_flashcards'),
    url(r'^ajax/user/(?P<username>[^/]+)/flashcards$', flashcards, name='ajax_user_flashcards'),
    url(r'^get-worklogs$', worklogs, name='worklogs'),
    url(r'^users$', users_list, name='users'),
    url(r'^ajax/users$', users_list, name='ajax_users'),
    url(r'^user/(?P<username>[^/]+)$', profile_view, name='user'),
    url(r'^ajax/user/(?P<username>[^/]+)$', profile_view, name='ajax_user'),
    url(r'^update-profile$', update_profile, name='update_profile'),
    url(r'^user/(?P<username>[^/]+)/card-order$', card_order, name='card_order'),
    url(r'^login$', log_in, name='login'),
    url(r'^logout$', log_out, name='logout'),

    url(r'^oauth/', include('social_django.urls', namespace='social')),
    url(r'^schedule/', include('schedule.urls')),
    url(r'^sitemap\.xml$', sitemap, {'sitemaps': sitemaps},
        name='django.contrib.sitemaps.views.sitemap'),
    url(r'^admin/', include(admin.site.urls)),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
