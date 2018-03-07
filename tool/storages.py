from gzip import GzipFile
import mimetypes

from django.conf import settings
from django.utils import timezone
from django.utils.encoding import force_bytes
from django.utils.six import BytesIO
from google.cloud.exceptions import NotFound
from storages.backends.gcloud import GoogleCloudFile, GoogleCloudStorage
from storages.utils import clean_name


class ToolCloudFile(GoogleCloudFile):
    def _get_file(self):
        self._file = super()._get_file()
        if self._storage.gzip:
            self._file = GzipFile(mode=self._mode, fileobj=self._file,
                                  mtime=0.0)
        return self._file


class ToolStorage(GoogleCloudStorage):
    default_content_type = 'application/octet-stream'
    gzip = True
    gzip_content_types = (
        'text/css',
        'text/javascript',
        'application/javascript',
        'application/x-javascript',
        'image/svg+xml',
    )

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

    def url(self, name):
        try:
            return super().url(name)
        except NotFound:
            return None

    def _compress_content(self, content):
        """ Gzip a given string content. """
        content.seek(0)
        zbuf = BytesIO()
        #  The GZIP header has a modification time attribute
        # (see http://www.zlib.org/rfc-gzip.html)
        #  This means each time a file is compressed it changes even
        # if the other contents don't change
        #  Fixing the mtime at 0.0 at compression time avoids this problem
        zfile = GzipFile(mode='wb', compresslevel=6, fileobj=zbuf, mtime=0.0)
        try:
            zfile.write(force_bytes(content.read()))
        finally:
            zfile.close()
        zbuf.seek(0)

        return zbuf

    def _open(self, name, mode='rb'):
        name = self._normalize_name(clean_name(name))
        file_object = ToolCloudFile(name, mode, self)
        if not file_object.blob:
            raise IOError(u'File does not exist: %s' % name)
        return file_object

    def _save(self, name, content):
        _type, encoding = mimetypes.guess_type(name)
        content_type = getattr(content, 'content_type', None)
        content_type = content_type or _type or self.default_content_type

        if self.gzip and content_type in self.gzip_content_types:
            content = self._compress_content(content)

        cleaned_name = clean_name(name)
        name = self._normalize_name(cleaned_name)

        content.name = cleaned_name
        encoded_name = self._encode_name(name)
        file = ToolCloudFile(encoded_name, 'rw', self)
        file.blob.upload_from_file(content, content_type=content_type)
        if encoding:
            file.blob.content_encoding = encoding
            file.blob.patch()
        return cleaned_name
