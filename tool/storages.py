from django.conf import settings
from django.utils import timezone
from storages.backends.gcloud import GoogleCloudStorage
from storages.utils import clean_name


class ToolStorage(GoogleCloudStorage):
    def _normalize_name(self, name):
        """ Normalizes the name. """
        return '{}/{}'.format(settings.SITE_ENV_PREFIX.lower(),
                              super()._normalize_name(name))

    def get_created_time(self, name):
        """
        Return the creation time (as a datetime) of the file specified by name.
        The datetime will be timezone-aware if USE_TZ=True.
        """
        name = self._normalize_name(clean_name(name))
        blob = self._get_blob(self._encode_name(name))
        return timezone.make_naive(blob.time_created)
