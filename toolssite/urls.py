"""toolssite URL Configuration
"""
from django.conf.urls import include, url
from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.sitemaps.views import sitemap

from tool.views import tool, worklogs, flashcards, dictionary, card_order
from tool.sitemaps import StaticViewSitemap

sitemaps = {
    'static': StaticViewSitemap,
}


urlpatterns = [
    url(r'^$', tool, name='main', kwargs={'slug': 'jira-logs'}),
    url(r'^ajax$', tool, name='ajax_main', kwargs={'slug': 'jira-logs'}),
    url(r'^tool/(?P<slug>.+)$', tool, name='tool'),
    url(r'^ajax/tool/(?P<slug>.+)$', tool, name='ajax_tool'),
    url(r'^flashcards$', flashcards, name='flashcards'),
    url(r'^flashcards/(?P<username>.+)$', flashcards, name='flashcards_username'),
    url(r'^ajax/flashcards$', flashcards, name='ajax_flashcards'),
    url(r'^ajax/flashcards/(?P<username>.+)$', flashcards, name='ajax_flashcards_username'),
    url(r'^dictionary$', dictionary, name='dictionary'),
    url(r'^dictionary/(?P<username>.+)$', dictionary, name='dictionary_username'),
    url(r'^ajax/dictionary$', dictionary, name='ajax_dictionary'),
    url(r'^ajax/dictionary/(?P<username>.+)$', dictionary, name='ajax_dictionary_username'),
    url(r'^get-worklogs$', worklogs, name='worklogs'),
    url(r'^user/(?P<username>.+)/card-order$', card_order, name='card_order'),

    url(r'^sitemap\.xml$', sitemap, {'sitemaps': sitemaps},
        name='django.contrib.sitemaps.views.sitemap'),
    url(r'^admin/', include(admin.site.urls)),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
