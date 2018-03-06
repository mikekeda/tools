from storages.backends.gcloud import GoogleCloudStorage
from django.conf import settings


class ToolStorage(GoogleCloudStorage):
    def _normalize_name(self, name):
        """ Normalizes the name. """
        return '{}/{}'.format(settings.SITE_ENV_PREFIX.lower(),
                              super()._normalize_name(name))
