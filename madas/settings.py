# Django settings for madas project.
import os

from django.utils.webhelpers import url
if not os.environ.has_key('PROJECT_DIRECTORY'):
	os.environ['PROJECT_DIRECTORY']=os.path.dirname(__file__)
if not os.environ.has_key('SCRIPT_NAME'):								# this will be missing if we are running on the internal server
	os.environ['SCRIPT_NAME']=''
PROJECT_DIRECTORY = os.environ['PROJECT_DIRECTORY']
SCRIPT_NAME = os.environ['SCRIPT_NAME']

DEBUG = True
TEMPLATE_DEBUG = DEBUG

ADMINS = (
    ('Tech Alerts', 'alerts@ccg.murdoch.edu.au'),
)

MANAGERS = ADMINS


# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# If running in a Windows environment this must be set to the same as your
# system time zone.
TIME_ZONE = 'Australia/Perth'

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'en-us'


# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

# Absolute path to the directory that holds media.
# Example: "/home/media/media.lawrence.com/"
MEDIA_ROOT = os.path.join(PROJECT_DIRECTORY, 'static')

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash if there is a path component (optional in other cases).
# Examples: "http://media.lawrence.com", "http://example.com/media/"
MEDIA_URL = '/django-temp/'

# URL prefix for admin media -- CSS, JavaScript and images. Make sure to use a
# trailing slash.
# Examples: "http://foo.com/media/", "/media/".
ADMIN_MEDIA_PREFIX = '/admin-media/'

# Make this unique, and don't share it with anybody.
SECRET_KEY = 'qj#tl@9@7((%^)$i#iyw0gcfzf&#a*pobgb8yr#1%65+*6!@g$'

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.load_template_source',
    'django.template.loaders.app_directories.load_template_source',
#     'django.template.loaders.eggs.load_template_source',
)

MIDDLEWARE_CLASSES = (
    'django.middleware.email.EmailExceptionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    #'django.middleware.doc.XViewMiddleware',
    'django.middleware.ssl.SSLRedirect'
)

# a directory that will be writable by the webserver, for storing various files...
WRITABLE_DIRECTORY = os.path.join(PROJECT_DIRECTORY,"scratch")

# Captcha image directory
CAPTCHA_IMAGES = os.path.join(WRITABLE_DIRECTORY, "captcha")

##
## Mako settings stuff
##

# extra mako temlate directories
MAKO_TEMPLATE_DIRS = ( os.path.join(PROJECT_DIRECTORY,"templates","mako"), )

# mako compiled templates directory
MAKO_MODULE_DIR = os.path.join(WRITABLE_DIRECTORY, "templates")

# mako module name
MAKO_MODULENAME_CALLABLE = ''

##
## memcache server list
##
MEMCACHE_SERVERS = ['memcache1.localdomain:11211','memcache2.localdomain:11211']
MEMCACHE_KEYSPACE = ""

##
## CAPTCHA settings
##
# the filesystem space to write the captchas into
CAPTCHA_ROOT = os.path.join(MEDIA_ROOT, 'captchas')

# the URL base that points to that directory served out
CAPTCHA_URL = os.path.join(MEDIA_URL, 'captchas')



# development deployment
if "DJANGODEV" in os.environ:
    DEBUG = True if os.path.exists(os.path.join(PROJECT_DIRECTORY,".debug")) else ("DJANGODEBUG" in os.environ)
    TEMPLATE_DEBUG = DEBUG
    DATABASE_ENGINE = 'postgresql_psycopg2'           # 'postgresql_psycopg2', 'postgresql', 'mysql', 'sqlite3' or 'ado_mssql'.
    DATABASE_NAME = 'dev_madas'             # Or path to database file if using sqlite3.
    DATABASE_USER = 'madasapp'             # Not used with sqlite3.
    DATABASE_PASSWORD = 'madasapp'         # Not used with sqlite3.
    DATABASE_HOST = 'eowyn.localdomain'             # Set to empty string for localhost. Not used with sqlite3.
    SSL_ENABLED = True
    if "LOCALDEV" in os.environ:
        SSL_ENABLED = False
    DEV_SERVER = True

    # debug site table
    SITE_ID = 1

    #####################################################################################################
    # Application Variables
    #####################################################################################################
    APPEND_SLASH = False                    #This is a django config variable. 
    SITE_NAME = 'madas'
    RETURN_EMAIL = 'bpower@ccg.murdoch.edu.au'
    DEFAULT_GROUP = 'madas'  #this needs to exist in the database.
    AUTH_LDAP_SERVER = 'ldaps://fds3.localdomain'
    AUTH_LDAP_ADMIN_BASE = 'dc=ccg,dc=murdoch,dc=edu,dc=au'
    AUTH_LDAP_BASE = 'ou=People,dc=ccg,dc=murdoch,dc=edu,dc=au'
    AUTH_LDAP_GROUP_BASE = 'ou=NEMA,ou=Web Groups,dc=ccg,dc=murdoch,dc=edu,dc=au'
    AUTH_LDAP_USER_BASE = 'ou=NEMA,ou=People,' + AUTH_LDAP_ADMIN_BASE
    AUTH_LDAP_GROUP = 'User'
    LDAPADMINUSERNAME = 'uid=nemaapp,ou=Application Accounts'
    LDAPADMINPASSWORD = 'nr2WovGfkWR'
    MADAS_STATUS_GROUPS = ['User', 'Pending', 'Deleted', 'Rejected']
    MADAS_ADMIN_GROUPS = ['Administrators', 'Node Reps']
    SESSION_TIMEOUT = 600 #10 minute session timeout
    #####################################################################################################



# production deployment (probably using wsgi)
else:
    DEBUG = os.path.exists(os.path.join(PROJECT_DIRECTORY,".debug"))
    TEMPLATE_DEBUG = DEBUG
    DATABASE_ENGINE = 'postgresql_psycopg2'           # 'postgresql_psycopg2', 'postgresql', 'mysql', 'sqlite3' or 'ado_mssql'.
    DATABASE_NAME = 'live_madas'             # Or path to database file if using sqlite3.
    DATABASE_USER = 'madasapp'             # Not used with sqlite3.
    DATABASE_PASSWORD = 'madasapp'         # Not used with sqlite3.
    DATABASE_HOST = 'iridium.localdomain'             # Set to empty string for localhost. Not used with sqlite3.
    DATABASE_PORT = ''             # Set to empty string for default. Not used with sqlite3.
    SSL_ENABLED = True
    DEV_SERVER = False

    # production site id
    SITE_ID = 1

    #####################################################################################################
    # Application Variables
    #####################################################################################################
    APPEND_SLASH = False                    #This is a django config variable. 
    SITE_NAME = 'madas'
    RETURN_EMAIL = 'techs@ccg.murdoch.edu.au'
    DEFAULT_GROUP = 'madas'  #this needs to exist in the database.
    AUTH_LDAP_SERVER = 'ldaps://fds3.localdomain'
    AUTH_LDAP_ADMIN_BASE = 'dc=ccg,dc=murdoch,dc=edu,dc=au'
    AUTH_LDAP_BASE = 'ou=People,dc=ccg,dc=murdoch,dc=edu,dc=au'
    AUTH_LDAP_GROUP_BASE = 'ou=NEMA,ou=Web Groups,dc=ccg,dc=murdoch,dc=edu,dc=au'
    AUTH_LDAP_USER_BASE = 'ou=NEMA,ou=People,' + AUTH_LDAP_ADMIN_BASE
    AUTH_LDAP_GROUP = 'User'
    LDAPADMINUSERNAME = 'uid=nemaapp,ou=Application Accounts'
    LDAPADMINPASSWORD = 'nr2WovGfkWR'
    MADAS_STATUS_GROUPS = ['User', 'Pending', 'Deleted', 'Rejected']
    MADAS_ADMIN_GROUPS = ['Administrators', 'Node Reps']
    SESSION_TIMEOUT = 600 #10 minute session timeout
    #####################################################################################################


# email server
EMAIL_HOST = 'ccg.murdoch.edu.au'
EMAIL_APP_NAME = "Madas (Mango)"
SERVER_EMAIL = "apache@ccg.murdoch.edu.au"
EMAIL_SUBJECT_PREFIX = "Madas (Mango) %s %s:"%("DEBUG" if DEBUG else "","DEV_SERVER" if DEV_SERVER else "")



ROOT_URLCONF = 'madas.urls'

#LOGIN_URL = url('/login')

TEMPLATE_DIRS = (
    # Put strings here, like "/home/html/django_templates" or "C:/www/django/templates".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
    os.path.join(PROJECT_DIRECTORY,"templates","mako"),
)

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.admin',
    'madas.m',
    'madas.dashboard',
    'madas.login',
    'madas.quote',
    'madas.users',
    'madas.admin'
)




AUTHENTICATION_BACKENDS = (
 'madas.ccgauth.LDAPBackend',
 'django.contrib.auth.backends.ModelBackend',
)

# for local development, this is set to the static serving directory. For deployment use Apache Alias
STATIC_SERVER_PATH = os.path.join(PROJECT_DIRECTORY,"static")
