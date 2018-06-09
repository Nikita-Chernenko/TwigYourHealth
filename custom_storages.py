from django.conf import settings
from dropbox.exceptions import ApiError
from storages.backends.dropbox import DropBoxStorage


class MyStorage(DropBoxStorage):
    def url(self, name):
        try:
            return super(MyStorage, self).url(name)
        except ApiError:
            return None
