"""
Tools site URL Configuration
"""
from django.conf.urls import include
from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.sitemaps.views import sitemap
from django.urls import path
from django.utils.translation import ugettext_lazy as _

from tool.views import (tool, calendar, dictionary, flashcards, users_list,
                        profile_view, update_profile, user_events, card_order,
                        task_order, FlightsView, tasks_view, CanvasView,
                        CanvasesView, CodeView, log_in, log_out)
from tool.sitemaps import StaticViewSitemap

sitemaps = {
    'static': StaticViewSitemap,
}


urlpatterns = [
    path('', tool, name='main', kwargs={'slug': 'text'}),
    path('ajax', tool, name='ajax_main', kwargs={'slug': 'text'}),
    path('tool/<str:slug>', tool, name='tool'),
    path('ajax/tool/<str:slug>', tool, name='ajax_tool'),
    path('user/<str:username>/tool/<str:slug>', tool, name='user_tool'),
    path('ajax/user/<str:username>/tool/<str:slug>', tool, name='ajax_user_tool'),
    path('calendar', calendar, name='calendar'),
    path('ajax/calendar', calendar, name='ajax_calendar'),
    path('user/<str:username>/calendar', calendar, name='user_calendar'),
    path('ajax/user/<str:username>/calendar', calendar, name='ajax_user_calendar'),
    path('dictionary', dictionary, name='dictionary'),
    path('ajax/dictionary', dictionary, name='ajax_dictionary'),
    path('user/<str:username>/dictionary', dictionary, name='user_dictionary'),
    path('ajax/user/<str:username>/dictionary', dictionary, name='ajax_user_dictionary'),
    path('flashcards', flashcards, name='flashcards'),
    path('ajax/flashcards', flashcards, name='ajax_flashcards'),
    path('user/<str:username>/flashcards', flashcards, name='user_flashcards'),
    path('ajax/user/<str:username>/flashcards', flashcards, name='ajax_user_flashcards'),
    path('tasks', tasks_view, name='tasks'),
    path('ajax/tasks', tasks_view, name='ajax_tasks'),
    path('user/<str:username>/tasks', tasks_view, name='user_tasks'),
    path('ajax/user/<str:username>/tasks', tasks_view, name='ajax_user_tasks'),
    path('user/<str:username>/canvases', CanvasesView.as_view(), name='canvases'),
    path('canvas/<str:slug>', CanvasView.as_view(), name='canvas'),
    path('flights', FlightsView.as_view(), name='flights'),
    path('ajax/flights', FlightsView.as_view(), name='ajax_flights'),
    path('code', CodeView.as_view(), name='code'),
    path('ajax/code', CodeView.as_view(), name='ajax_code'),
    path('code/<str:slug>', CodeView.as_view(), name='code_slug'),
    path('ajax/code/<str:slug>', CodeView.as_view(), name='ajax_code_slug'),
    path('users', users_list, name='users'),
    path('ajax/users', users_list, name='ajax_users'),
    path('user/<str:username>', profile_view, name='user'),
    path('ajax/user/<str:username>', profile_view, name='ajax_user'),
    path('update-profile', update_profile, name='update_profile'),
    path('events', user_events, name='events'),
    path('user/<str:username>/card-order', card_order, name='card_order'),
    path('user/<str:username>/task-order', task_order, name='task_order'),
    path('login', log_in, name='login'),
    path('logout', log_out, name='logout'),

    path('oauth/', include('social_django.urls', namespace='social')),
    path('schedule/', include('schedule.urls')),
    path('sitemap.xml', sitemap, {'sitemaps': sitemaps},
         name='django.contrib.sitemaps.views.sitemap'),
    path('admin/', admin.site.urls),
]
admin.site.site_header = _('Tools administration')

if settings.DEBUG:
    urlpatterns += static(
        settings.MEDIA_URL,
        document_root=settings.MEDIA_ROOT
    )
