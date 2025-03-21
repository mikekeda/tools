"""
Tools site URL Configuration
"""

from django.conf import settings
from django.conf.urls import include
from django.contrib import admin
from django.contrib.sitemaps.views import sitemap
from django.urls import path
from django.utils.translation import gettext_lazy as _

from tool.sitemaps import StaticViewSitemap
from tool.views.views import (
    CalendarView,
    CanvasesView,
    CanvasView,
    CodeView,
    DictionaryView,
    FakeCheckView,
    FlashcardsView,
    LinkView,
    ProfileView,
    TasksView,
    TracerouteView,
    about_page,
    card_order,
    link_order,
    log_in,
    log_out,
    task_order,
    tool,
    user_events,
    users_list,
    ShoppingListsView,
    ShoppingListView,
)

sitemaps = {
    "static": StaticViewSitemap,
}


urlpatterns = [
    path("", tool, name="main", kwargs={"slug": "text-manipulation"}),
    path("ajax", tool, name="ajax_main", kwargs={"slug": "text-manipulation"}),
    path("tool/<str:slug>", tool, name="tool"),
    path("ajax/tool/<str:slug>", tool, name="ajax_tool"),
    path("user/<str:username>/tool/<str:slug>", tool, name="user_tool"),
    path("ajax/user/<str:username>/tool/<str:slug>", tool, name="ajax_user_tool"),
    path("calendar", CalendarView.as_view(), name="calendar"),
    path("ajax/calendar", CalendarView.as_view(), name="ajax_calendar"),
    path("user/<str:username>/calendar", CalendarView.as_view(), name="user_calendar"),
    path(
        "ajax/user/<str:username>/calendar",
        CalendarView.as_view(),
        name="ajax_user_calendar",
    ),
    path("calendar/<int:pk>", CalendarView.as_view(), name="calendar_pk"),
    path("ajax/calendar/<int:pk>", CalendarView.as_view(), name="ajax_calendar_pk"),
    path(
        "user/<str:username>/calendar/<int:pk>",
        CalendarView.as_view(),
        name="user_calendar_pk",
    ),
    path(
        "ajax/user/<str:username>/calendar/<int:pk>",
        CalendarView.as_view(),
        name="ajax_user_calendar_pk",
    ),
    path("dictionary", DictionaryView.as_view(), name="dictionary"),
    path("ajax/dictionary", DictionaryView.as_view(), name="ajax_dictionary"),
    path(
        "user/<str:username>/dictionary",
        DictionaryView.as_view(),
        name="user_dictionary",
    ),
    path(
        "ajax/user/<str:username>/dictionary",
        DictionaryView.as_view(),
        name="ajax_user_dictionary",
    ),
    path("flashcards", FlashcardsView.as_view(), name="flashcards"),
    path("ajax/flashcards", FlashcardsView.as_view(), name="ajax_flashcards"),
    path(
        "user/<str:username>/flashcards",
        FlashcardsView.as_view(),
        name="user_flashcards",
    ),
    path(
        "ajax/user/<str:username>/flashcards",
        FlashcardsView.as_view(),
        name="ajax_user_flashcards",
    ),
    path("flashcards/<int:pk>", FlashcardsView.as_view(), name="flashcards_pk"),
    path(
        "ajax/flashcards/<int:pk>", FlashcardsView.as_view(), name="ajax_flashcards_pk"
    ),
    path("tasks", TasksView.as_view(), name="tasks"),
    path("ajax/tasks", TasksView.as_view(), name="ajax_tasks"),
    path("user/<str:username>/tasks", TasksView.as_view(), name="user_tasks"),
    path("ajax/user/<str:username>/tasks", TasksView.as_view(), name="ajax_user_tasks"),
    path("tasks/<int:pk>", TasksView.as_view(), name="tasks_pk"),
    path("ajax/tasks/<int:pk>", TasksView.as_view(), name="ajax_tasks_pk"),
    path("user/<str:username>/canvases", CanvasesView.as_view(), name="canvases"),
    path("canvas/<str:slug>", CanvasView.as_view(), name="canvas"),
    path("code", CodeView.as_view(), name="code"),
    path("ajax/code", CodeView.as_view(), name="ajax_code"),
    path("traceroute", TracerouteView.as_view(), name="traceroute"),
    path("ajax/traceroute", TracerouteView.as_view(), name="ajax_traceroute"),
    path("news-check", FakeCheckView.as_view(), name="news_check"),
    path("ajax/news-check", FakeCheckView.as_view(), name="ajax_news_check"),
    path("user/<str:username>/code", CodeView.as_view(), name="user_code"),
    path("ajax/user/<str:username>/code", CodeView.as_view(), name="ajax_user_code"),
    path("code/<str:slug>", CodeView.as_view(), name="code_slug"),
    path("ajax/code/<str:slug>", CodeView.as_view(), name="ajax_code_slug"),
    path("shopping_lists", ShoppingListsView.as_view(), name="shopping_lists"),
    path("shopping_lists/<int:pk>", ShoppingListView.as_view(), name="shopping_list"),
    path(
        "ajax/shopping_lists", ShoppingListsView.as_view(), name="ajax_shopping_lists"
    ),
    path(
        "ajax/shopping_lists/<int:pk>",
        ShoppingListView.as_view(),
        name="ajax_shopping_list",
    ),
    path("links", LinkView.as_view(), name="links"),
    path("ajax/links", LinkView.as_view(), name="ajax_links"),
    path("links/<int:pk>", LinkView.as_view(), name="links_pk"),
    path("ajax/links/<int:pk>", LinkView.as_view(), name="ajax_links_pk"),
    path("user/<str:username>/links", LinkView.as_view(), name="user_links"),
    path("ajax/user/<str:username>/links", LinkView.as_view(), name="ajax_user_links"),
    path("users", users_list, name="users"),
    path("ajax/users", users_list, name="ajax_users"),
    path("user/<str:username>", ProfileView.as_view(), name="user"),
    path("ajax/user/<str:username>", ProfileView.as_view(), name="ajax_user"),
    path("events", user_events, name="events"),
    path("user/<str:username>/card-order", card_order, name="card_order"),
    path("user/<str:username>/task-order", task_order, name="task_order"),
    path("user/<str:username>/link-order", link_order, name="link_order"),
    path("about", about_page, name="about_page"),
    path("ajax/about", about_page, name="ajax_about_page"),
    path("login", log_in, name="login"),
    path("ajax/login", log_in, name="ajax_login"),
    path("logout", log_out, name="logout"),
    path("oauth/", include("social_django.urls", namespace="social")),
    path("schedule/", include("schedule.urls")),
    path(
        "sitemap.xml",
        sitemap,
        {"sitemaps": sitemaps},
        name="django.contrib.sitemaps.views.sitemap",
    ),
    path("admin/", admin.site.urls),
]
admin.site.site_header = _("Tools administration")

if settings.DEBUG:
    import debug_toolbar
    from django.conf.urls.static import static

    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += [path("__debug__/", include(debug_toolbar.urls))]
