.. _site_configuration:

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

**EMAIL_HOST** = "example - smtp.yoursite.com"
    You should replace this string with the name of your mail server.
**SERVER_EMAIL** = "example - apache@yoursite.com"
    This should be the email address which shows up as the 'From email' in emails from this webapp to users. 
**RETURN_EMAIL** = "example - noreply@yoursite.com"
    This is the return address, i.e. the email address that would be used if users replied to webapp emails.
**EMAIL_SUBJECT_PREFIX** = "DEV "
    This is a prefix for the subject line of the email, often used to differentiate emails from the live system from development system emails.
**LOGS_TO_EMAIL** = "log_email@yoursite.com"
    When a user clicks the 'Send Logs' button on the :ref:`sync client <datasync_client>`, this is the email address that gets notified. 
**KEYS_TO_EMAIL** = "key_email@yoursite.com"
    When the :ref:`sync client <datasync_client>` 'Send Keys' button is pressed, this email addres is notified.
**SECRET_KEY** = 'some random string'
    Key used for site hashing algorithms. Set this to a random string.
**DATABASES** = {a database dictionary}
    This is a python dictionary which defines how django should connect to the database

Example::
    
    {
        'default': {
            'ENGINE': 'django.db.backends.postgresql_psycopg2',
            'NAME': '<your database name here>',
            'USER': '<your database user here>',
            'PASSWORD': '<your database user password here>',
            'HOST': '<your database host here>',                      
            'PORT': '',                      
        }
    }

    #The ENGINE setting here describes a postgres database connection
    #NAME is the database name
    #USER is the database user
    #PASSWORD is the database user password
    #HOST/PORT describes your servers hostname and port.



.. _site_configuration_optional_variables:

Optional Variable Overrides
===========================

**TMP_DIRECTORY** = os.path.join(PROJECT_DIRECTORY, 'tmp')
    This must be a writeable directory where temporary files will be stored.
**DEBUG** = True
    Defines (among other things) how error messages are shown and what information is exposed. Should be False for production servers.
    
**SSL_ENABLED** = True
    Enables/Disables the SSLRedirectMiddleware. Should be False only for development, should be True on production servers.

**PERSISTENT_FILESTORE** = os.path.normpath(os.path.join(PROJECT_DIRECTORY, '..', '..', 'files'))
    An area of the filesystem for the application to write persistent data - quotes, experiment files, user uploads etc. More on the persistent filestore is covered in :ref:`Persistent Filestore <persistent_filestore>`
**MADAS_SESSION_TIMEOUT** = 1800
    Web session timeout - Defaults to 30 mins.
**CHMOD_USER** = 'apache'
    The UNIX user who should own files created by this application. If this is not the user who is running the webserver, that user should at least be in the group mentioned below, or the application will not be able to read the files it has written.
**CHMOD_GROUP** = 'maupload'
    The UNIX group who should own files created by this webapp. The user who runs the webserver should be a member of this group. This is important not onlu if CHMOD_USER is not the webserver user, but also because the :ref:`datasync <datasync_client>` process may create files not owned by the webserver user, but they will always be owned by this group.

