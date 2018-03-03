import re

from django.core.validators import RegexValidator

comma_separated_field = RegexValidator(
    regex='^([\w ]+ {0,2}, {0,2})*([\w ]+ {0,2})$',
    message='Should countain names separated with coma(spaces are available)', flags=re.UNICODE
)
