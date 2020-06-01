from django.contrib import sitemaps
from django.urls import reverse

from tool.context_processors import categories


class StaticViewSitemap(sitemaps.Sitemap):
    priority = 0.5
    changefreq = 'weekly'

    def items(self):
        return [tool['slug'] for tool in categories()['tools']] + ['about_page', 'news_check']

    def location(self, obj):
        if obj in {'about_page', 'news_check'}:
            return reverse(obj)
        return reverse('tool', kwargs={'slug': obj})
