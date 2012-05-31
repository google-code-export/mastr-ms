.. _persistent_filestore:
Persistent Filestore
====================

As well as storing site data in a database, the Mastr-MS site stores other persistent data as files in the filesystem. This file storage area is referred to as the Persistent Filestore.

The scripts associated with site [siteconfig | Site Configuration] contains the PERSISTENT_FILESTORE variable, which by default is set to a directory called 'files', which is on the same level as the app deployment director(ies). Two other configuration variables are important:  
