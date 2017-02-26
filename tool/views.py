from django.shortcuts import render
from django.http import Http404


def main(request):
    """Main page."""

    return render(request, "slider.html", dict(active_page="home"))


def tool(request, page_slug):
    """Tool."""

    try:
        return render(request, page_slug + ".html", dict(active_page=page_slug))
    except Exception:
        raise Http404
