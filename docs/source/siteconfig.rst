Site Configuration
==================

The Mastr-MS site variables are defined in the settings.py file found within the application root. Many of these have sensible defaults, but some need to be populated in order for the site to work - database settings, email servers etc. This can be done in the settings.py file directly, although this is not advised, since redeploying the site or any updates to the source code will overwrite your custom settings. The best strategy is to leverage the final import statement in the settings.py file, which is used to pull in deployment specific overrides::

    # Override defaults with your local instance settings.
    # They will be loaded from appsettings.<projectname>, which can exist anywhere
    # in the instance's pythonpath. This is a CCG convention designed to support
    # global shared settings among multiple Django projects.
    try:
        from appsettings.mastrms import *
    except ImportError, e:
        pass

This means you can create an appsettings.mastrms module anywhere accessible to this app (using PYTHONPATH for example). The file structure would look like this:

| appsettings
|     __init__.py
|     mastrms
|         __init__.py

Then, all your overrides go in the mastrms __init__.py

Required Variable Overrides
===========================
**EMAIL_HOST** = "<insert email host here>"
    This is the email host blah
**SERVER_EMAIL** = "<email address of >"                      # from address
    The from address
**RETURN_EMAIL** = "apache@ccg.murdoch.edu.au"                      # from address
    The return address
**EMAIL_SUBJECT_PREFIX** = "DEV "
    Blah
**RETURN_EMAIL** = 'bpower@ccg.murdoch.edu.au'
    Blah
**LOGS_TO_EMAIL** = "<email address to receive datasync client log notifications>"
    Blah
**KEYS_TO_EMAIL** = "<email address to receive datasync key upload notifications>"
    Blah
**SECRET_KEY** = 'qj#tl@9@7((%^)$i#iyw0gcfzf&#a*pobgb8yr#1%65+*6!@g$'
    Blah
**DATABASES** = {
|    'default': {
|        'ENGINE': 'django.db.backends.postgresql_psycopg2',
|        'NAME': '<your database name here>',
|        'USER': '<your database user here>',
|        'PASSWORD': '<your database user password here>',
|        'HOST': '<your database host here>',                      
|        'PORT': '',                      
|    }
| }




Optional Variable Overrides
=========================
**TMP_DIRECTORY** = os.path.join(PROJECT_DIRECTORY, 'tmp')
    Blah
**DEBUG** = True
    Blah
**DEV_SERVER** = True
    Blah
**SSL_ENABLED** = True
    Blah
**PERSISTENT_FILESTORE** = os.path.normpath(os.path.join(PROJECT_DIRECTORY, '..', '..', 'files'))
    Blah
**MADAS_SESSION_TIMEOUT** = 1800
    Blah
**CHMOD_USER** = 'apache'
    Blah
**CHMOD_GROUP** = 'maupload'
    Blah

