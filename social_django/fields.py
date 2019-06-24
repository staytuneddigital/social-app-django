import ast
import json
import six

from django.core.exceptions import ValidationError
from django.conf import settings
from django.db import models
from django.utils.encoding import force_text

# assume we have pgcrypto installed in DB.
from pgcrypto.fields import TextPGPSymmetricKeyField

from social_core.utils import setting_name

if getattr(settings, setting_name('POSTGRES_JSONFIELD'), False):
    from django.contrib.postgres.fields import JSONField as JSONFieldBase
else:
    JSONFieldBase = models.TextField


import environ

# Read settings from the environment.
env = environ.Env()


SECRET_KEY = env('DJANGO_SECRET_KEY')


class JSONField(JSONFieldBase):
    """Simple JSON field that stores python structures as JSON strings
    on database.
    """

    def __init__(self, *args, **kwargs):
        kwargs.setdefault('default', dict)
        super(JSONField, self).__init__(*args, **kwargs)

    def from_db_value(self, value, *args, **kwargs):
        return self.to_python(value)

    def to_python(self, value):
        """
        Convert the input JSON value into python structures, raises
        django.core.exceptions.ValidationError if the data can't be converted.
        """
        if self.blank and not value:
            return {}
        value = value or '{}'
        if isinstance(value, six.binary_type):
            value = six.text_type(value, 'utf-8')
        if isinstance(value, six.string_types):
            try:
                return json.loads(value)
            except Exception as err:
                raise ValidationError(str(err))
        else:
            return value

    def validate(self, value, model_instance):
        """Check value is a valid JSON string, raise ValidationError on
        error."""
        if isinstance(value, six.string_types):
            super(JSONField, self).validate(value, model_instance)
            try:
                json.loads(value)
            except Exception as err:
                raise ValidationError(str(err))

    def get_prep_value(self, value):
        """Convert value to JSON string before save"""
        try:
            return json.dumps(value)
        except Exception as err:
            raise ValidationError(str(err))

    def value_to_string(self, obj):
        """Return value from object converted to string properly"""
        return force_text(self.value_from_object(obj))

    def value_from_object(self, obj):
        """Return value dumped to string."""
        orig_val = super(JSONField, self).value_from_object(obj)
        return self.get_prep_value(orig_val)


PGP_SYM_DECRYPT_SQL = f"""
    cast (pgp_sym_decrypt(%s::bytea, '{SECRET_KEY}') as text)
"""


print("\n\n\n *************** SECRET_KEY **************** \n\n\n")
print(SECRET_KEY)
print("\n\n\n ******************************************* \n\n\n")


class PGPEncryptedJSONAsTextField(TextPGPSymmetricKeyField, JSONField):
    """
    This class is an extension of the `TextPGPSymmetricKeyField`. It's meant to store JSONB as encrypted
    TEXT in the database. When decrypting, the JSONB is casted as `TEXT` because postgres cannot
    cast `BYTEA` -> `JSONB`. In lieu of that information, this class overrides the `from_db_value` method to convert
    the TEXT(JSONB) into a Python `dict` safely.
    """
    decrypt_sql = PGP_SYM_DECRYPT_SQL

    def db_type(self, connection=None):
        return self.cast_type

    def from_db_value(self, value, expression, connection):
        if isinstance(value, str):
            return ast.literal_eval(value)

        return value

    def to_python(self, value):
        return super(JSONField, self).to_python(value)
