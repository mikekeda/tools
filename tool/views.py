from django.shortcuts import render_to_response, get_object_or_404
from django.views.decorators.cache import cache_page
from django.views.decorators.http import etag
from django.template import RequestContext
from django.http import Http404


def main(request):
    """Main page."""

    return render_to_response("slider.html", dict(active_page="home"), context_instance=RequestContext(request))


def tool(request, page_slug):
    """Cakes related to category."""

    try:
        return render_to_response(page_slug + ".html", dict(active_page=page_slug), context_instance=RequestContext(request))
    except Exception, e:
        raise Http404
