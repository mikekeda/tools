from django.contrib import sitemaps
from django.urls import reverse

from .context_processors import categories


class StaticViewSitemap(sitemaps.Sitemap):
    priority = 0.5
    changefreq = 'weekly'

    def items(self):
        return [tool['slug'] for tool in categories()['tools']] + ['about']

    def location(self, obj):
        if obj == 'about':
            return reverse('about_page')
        return reverse('tool', kwargs={'slug': obj})
