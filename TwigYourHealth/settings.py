from .base_settings import *
import dj_database_url



DEBUG = False

ALLOWED_HOSTS = ['127.0.0.1', '.herokuapp.com']



DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'djangogirls',
        'USER': 'name',
        'PASSWORD': '',
        'HOST': 'localhost',
        'PORT': '',
    }
}

CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels_redis.core.RedisChannelLayer",
        "CONFIG": {
            "hosts": [("h:p570b412a20b87e2a84e1f98031515320a74d257a3c291716aeea796185260e43@ec2-18-207-51-51.compute-1.amazonaws.com", 11499)],
        },
    },
}

db_from_env = dj_database_url.config(conn_max_age=500)
DATABASES['default'].update(db_from_env)
