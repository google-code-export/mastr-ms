# -*- coding: utf-8 -*-
# Django settings for project.
import os
from django.utils.webhelpers import url

from appsettings.default_prod import *
from appsettings.mastrms.prod import *

# Defaults
#LOGIN_URL
#LOGIN_REDIRECT_URL
#LOGOUT_URL

ROOT_URLCONF = 'madas.urls'

INSTALLED_APPS.extend( [
    'madas.mdatasync_server',
    'madas.m',
    'madas.dashboard',
    'madas.login',
    'madas.quote',
    'madas.users',
    'madas.admin',
    'madas.repository'
] )

MADAS_STATUS_GROUPS = ['User', 'Pending', 'Deleted', 'Rejected']
MADAS_ADMIN_GROUPS = ['Administrators', 'Node Reps']

AUTHENTICATION_BACKENDS = [
 'madas.repository.backend.MadasBackend',
 #'django.contrib.auth.backends.LDAPBackend',
 'django.contrib.auth.backends.NoAuthModelBackend',
]

SESSION_COOKIE_PATH = url('/')
SESSION_SAVE_EVERY_REQUEST = True
CSRF_COOKIE_NAME = "csrftoken_madas_repoadmin"

PERSISTENT_FILESTORE = os.path.normpath(os.path.join(PROJECT_DIRECTORY, '..', '..', 'files'))

REPO_FILES_ROOT = PERSISTENT_FILESTORE
QUOTE_FILES_ROOT = os.path.join(PERSISTENT_FILESTORE, 'quotes')
MADAS_SESSION_TIMEOUT = 1800 #30 minute session timeout 

#Ensure the persistent storage dir exits. If it doesn't, exit noisily.
assert os.path.exists(PERSISTENT_FILESTORE), "This application cannot start: It expects a writeable directory at %s to use as a persistent filestore" % (PERSISTENT_FILESTORE) 

#functions to evaluate for status checking
from status_checks import *
STATUS_CHECKS = [check_default]

APPEND_SLASH = True
SITE_NAME = 'madas'

# these are non-standard and override defaults
MEDIA_ROOT = os.path.join(PROJECT_DIRECTORY,"static")
MEDIA_URL = '/static/'
