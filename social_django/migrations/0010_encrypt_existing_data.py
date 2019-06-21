# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings

from social_core.utils import setting_name


encrypt_existing_credentials_sql = '''
    update social_auth_usersocialauth
    set extra_data = cast (pgp_sym_encrypt(nullif(extra_data::text, NULL)::text, '{}') as text)
    where extra_data is not null
'''


class Migration(migrations.Migration):
    replaces = [
        ('default', '0010_encrypt_existing_data'),
        ('social_auth', '0010_encrypt_existing_data'),
    ]

    dependencies = [
        ('social_django', '0009_encrypted_extra_data'),
    ]

    operations = [
        migrations.RunSQL(encrypt_existing_credentials_sql),
    ]
