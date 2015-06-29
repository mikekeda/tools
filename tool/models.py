from django.db import models


class SimplePage(models.Model):
    """Simple Page model"""
    title = models.CharField(max_length=60, unique=True)
    body = models.TextField(blank=True, null=True)
    created_date = models.DateTimeField(auto_now_add=True)
    changed_date = models.DateTimeField(auto_now=True)
    slug = models.SlugField(blank=True, editable=True)

    def __unicode__(self):
        return u'%s' % (
            self.title,
        )
