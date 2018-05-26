from .base_settings import *
import dj_database_url

DEBUG = True

ALLOWED_HOSTS = ['*']

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
            "hosts": [
                "redis://h:p570b412a20b87e2a84e1f98031515320a74d257a3c291716aeea796185260e43@ec2-18-207-51-51.compute-1.amazonaws.com:11499"
            ],
        },
    },
}

db_from_env = dj_database_url.config()
DATABASES['default'].update(db_from_env)



AWS_S3_SECURE_URLS = False       # use http instead of https
AWS_QUERYSTRING_AUTH = False                # don't add complex authentication-related query parameters for requests
AWS_S3_ACCESS_KEY_ID = "AKIAJES67JKWUXXM6F5Q"                # Your S3 Access Key
AWS_S3_SECRET_ACCESS_KEY = "1daDfWxcMzxlcB+Dh/186x8sJkG2vqqU+BIrzlzc"            # Your S3 Secret
AWS_STORAGE_BUCKET_NAME = "twig-your-health.media"
AWS_S3_HOST = "s3-website.eu-west-3.amazonaws.com"  # Change to the media center you chose when creating the bucket

STATICFILES_STORAGE = "utils.s3.StaticS3BotoStorage"
DEFAULT_FILE_STORAGE = "utils.s3.MediaS3BotoStorage"

# the next monkey patch is necessary to allow dots in the bucket names
import ssl
if hasattr(ssl, '_create_unverified_context'):
   ssl._create_default_https_context = ssl._create_unverified_context