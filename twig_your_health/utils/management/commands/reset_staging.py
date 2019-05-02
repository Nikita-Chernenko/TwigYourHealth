from django.conf import settings
from django.core.management import call_command
from django.core.management.base import BaseCommand
from optparse import make_option
import os


class Command(BaseCommand):
    requires_model_validation = True

    def handle(self, *args, **options):
        for db_key in settings.DATABASES.keys():
            db_file = settings.DATABASES[db_key]['NAME']
            if os.path.exists(db_file):
                if not 'nodelete' in args:
                    os.unlink(db_file)

            kwargs = dict(database=db_key, interactive=False)
            kwargs['run_syncdb'] = True

            call_command('migrate', **kwargs)

        call_command('load_staging')
