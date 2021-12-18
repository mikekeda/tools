from __future__ import annotations

from django.contrib import sitemaps
from django.urls import reverse

from tool.context_processors import categories


class StaticViewSitemap(sitemaps.Sitemap):
    priority = 0.5
    changefreq = "weekly"

    def items(self) -> list[str]:
        return [tool["slug"] for tool in categories()["tools"]] + [
            "about_page",
            "news_check",
        ]

    def location(self, item: str) -> str:
        if item in {"about_page", "news_check"}:
            return reverse(item)
        return reverse("tool", kwargs={"slug": item})
