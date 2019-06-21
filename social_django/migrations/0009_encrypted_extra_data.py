# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings

from social_core.utils import setting_name

from social_django.fields import PGPEncryptedJSONAsTextField

USER_MODEL = getattr(settings, setting_name('USER_MODEL'), None) or \
             getattr(settings, 'AUTH_USER_MODEL', None) or \
             'auth.User'


class Migration(migrations.Migration):
    replaces = [
        ('default', '0009_encrypted_extra_data'),
        ('social_auth', '0009_encrypted_extra_data'),
    ]

    dependencies = [
        ('social_django', '0008_partial_timestamp'),
    ]

    operations = [
        migrations.AlterField(
            model_name='usersocialauth',
            name='extra_data',
            field=PGPEncryptedJSONAsTextField(default=''),
        )
    ]
