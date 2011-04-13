from django.utils import simplejson
from django.contrib.auth.ldap_helper import LDAPHandler
from django.contrib import logging
from madas.utils.data_utils import translate_dict, makeJsonFriendly

MADAS_USER_GROUP = 'User'
MADAS_PENDING_GROUP = 'Pending'
MADAS_DELETED_GROUP = 'Deleted'
MADAS_REJECTED_GROUP = 'Rejected'
MADAS_STATUS_GROUPS = [MADAS_USER_GROUP, MADAS_PENDING_GROUP, MADAS_DELETED_GROUP, MADAS_REJECTED_GROUP]
MADAS_ADMIN_GROUP = 'Administrators'
MADAS_NODEREP_GROUP = 'Node Reps'
MADAS_ADMIN_GROUPS = [MADAS_ADMIN_GROUP, MADAS_NODEREP_GROUP]

logger = logging.getLogger('madas_log')

#Just a class to encapsulate data to send to the frontend (as json)
class MAUser(object):
    def __init__(self, username):
        self._dict = {}
        self.Username = username
        self.IsLoggedIn = False
    @property 
    def IsAdmin(self):
        return self._dict.get('IsAdmin', False)
    @IsAdmin.setter
    def IsAdmin(self, value):
        self._dict['IsAdmin'] = value
    @property 
    def IsNodeRep(self):
        return self._dict.get('IsNodeRep', False)
    @IsNodeRep.setter 
    def IsNodeRep(self, value):
        self._dict['IsNodeRep'] = value
    @property 
    def IsClient(self):
        return self._dict.get('IsClient', False)
    @IsClient.setter 
    def IsClient(self, value):
        self._dict['IsClient'] = value
    @property 
    def IsStaff(self):
        return self._dict.get('IsStaff', False)
    @IsStaff.setter 
    def IsStaff(self, value):
        self._dict['IsStaff'] = value 
    @property 
    def IsLoggedIn(self):
        return self._dict.get('IsLoggedIn', False)
    @IsLoggedIn.setter 
    def IsLoggedIn(self, value):
        self._dict['IsLoggedIn'] = value
    @property 
    def Username(self):
        return self._dict.get('Username', False)
    @Username.setter 
    def Username(self, value):
        self._dict['Username'] = value
    @property
    def CachedGroups(self):
        groups = self._dict.get('CachedGroups', None)
        if groups == None:
            #we do a refresh
            self.refreshCachedGroups()
        return self._dict.get('CachedGroups', [])
    @CachedGroups.setter
    def CachedGroups(self, value):
        self._dict['CachedGroups'] = value
    
    @property
    def StatusGroup(self):
        return self._dict.get('StatusGroup', [])
    @StatusGroup.setter
    def StatusGroup(self, value):
        if isinstance(value, list):
            if len(value) > 0:
                value = value[0]
            else:
                value = None
        self._dict['StatusGroup'] = value
    @property
    def Nodes(self):
        return self._dict.get('Nodes', [])
    @Nodes.setter
    def Nodes(self, value):
        self._dict['Nodes'] = value
    
    @property 
    def CachedDetails(self):
        details = self._dict.get('CachedDetails', None)
        if details is None:
            #we do a refresh
            self.refreshCachedDetails()
        return self._dict.get('CachedDetails', {})
    @CachedDetails.setter
    def CachedDetails(self, value):
        self._dict['CachedDetails'] = value

    def refreshCachedGroups(self):
        logger.debug('\tNo cached groups for %s. Fetching.' % (self.Username) )
        groupsdict = getMadasUserGroups(self.Username)
        self.CachedGroups = groupsdict['groups'] + groupsdict['status']
        self.StatusGroup = groupsdict['status']
        return self.CachedGroups

    def refreshCachedDetails(self):
        logger.debug('\tRetrieving user details for %s.' % (self.Username) )
        detailsdict = getMadasUserDetails(self.Username)
        self.CachedDetails = dict(detailsdict)
        return self.CachedDetails
    
    def refresh(self):
        #defaults
        #IsLoggedIn is not handled here - it is managed by the getCurrentUser function
        self.IsAdmin = False
        self.IsClient = False
        self.IsNodeRep = False
        self.IsStaff = False

        #Grab groups, forcing a reload. 
        self.refreshCachedGroups()
        self.refreshCachedDetails()
        self.Nodes = getMadasNodeMemberships(self.CachedGroups)
            
        if MADAS_ADMIN_GROUP in self.CachedGroups:
            self.IsAdmin = True
        if MADAS_NODEREP_GROUP in self.CachedGroups:
            self.IsNodeRep = True
            
        #For 'staff':
        #They are not an admin
        #They are not a NodeRep
        #But they are part of some other group.
        #Note that all users are part of a 'User' group, so the test is:
        #!admin and !noderep and numgroups > 1
        if not self.IsAdmin and not self.IsNodeRep and len(self.CachedGroups) > 1:
            self.IsStaff = True
        elif len(self.CachedGroups) == 1 and MADAS_USER_GROUP in self.CachedGroups:
            self.IsClient = True

    def getData(self):
        return self._dict
    def toJson(self):
        return simplejson.dumps(self._dict)

#Gets the MAUser object out of the session, or creates a new one
def getCurrentUser(request, force_refresh = False):
    
    currentuser = request.session.get('mauser', False)
    if force_refresh or not currentuser: 
        currentuser = MAUser(request.user.username)
        currentuser.refresh()
        request.session['mauser'] = currentuser 
   
    #if the authentication is different:
    if currentuser.IsLoggedIn != request.user.is_authenticated():
        currentuser.IsLoggedIn = request.user.is_authenticated()
        request.session['mauser'] = currentuser 

    
    return request.session['mauser']

def getMadasUser(username):
    mauser = MAUser(username)
    mauser.refresh()
    return mauser


#Utility methods
def getMadasUserGroups(username, include_status_groups = False):
    ld = LDAPHandler()
    a = ld.ldap_get_user_groups(username)
    groups = []
    status = []
    
    if a:
        for name in a:
            if include_status_groups or name not in MADAS_STATUS_GROUPS:
                groups.append(name)

            #set the status group (even if being shown in 'groups')
            if name in MADAS_STATUS_GROUPS:
                status.append(name)
             
    return {'groups': groups, 'status': status}

def getMadasUsersFromGroups(grouplist, method='and') :
    '''Returns users who are a member of the groups given in grouplist
    The default 'method' is 'and', which will return only users who are a member
    of all groups. Passing 'or' will return users who are a member of any of the groups''' 
    ld = LDAPHandler()
    users = ld.ldap_list_users(grouplist, method)
    return users

def getMadasGroups():
    ldaphandler = LDAPHandler()
    ldapgroups = ldaphandler.ldap_list_groups()
    return ldapgroups

def getMadasNodeMemberships(groups):
    if groups is None:
        return []

    specialNodes = MADAS_STATUS_GROUPS + MADAS_ADMIN_GROUPS
    i = [item for item in groups if not item in specialNodes]
    return i

def getMadasUserDetails(username):
    ld = LDAPHandler()
    d = ld.ldap_get_user_details(username)
    #this is a function to un-listify values in the dict, since 
    #ldap often returns them that way
    def _stripArrays(inputdict):
        for key in inputdict.keys():
            if isinstance(inputdict[key], list):
                inputdict[key] = inputdict[key][0]
        return inputdict
    d = _stripArrays(d)
    return _translate_ldap_to_madas(d)

def _translate_madas_to_ldap(mdict):
    retdict = translate_dict(mdict, [('username', 'uid'), \
                           ('commonname', 'commonName'), \
                           ('firstname', 'givenName'), \
                           ('lastname', 'sn'), \
                           ('email', 'mail'), \
                           ('telephoneNumber', 'telephoneNumber'), \
                           ('homephone', 'homePhone'), \
                           ('physicalDeliveryOfficeName', 'physicalDeliveryOfficeName'), \
                           ('title', 'title'), \
                           ('dept', 'destinationIndicator'), \
                           ('areaOfInterest', 'description'), \
                           ('address', 'postalAddress'), \
                           ('institute', 'businessCategory'), \
                           ('supervisor', 'registeredAddress'), \
                           ('country', 'carLicense'), \
                            ])
    return retdict


def _translate_ldap_to_madas(ldict):
    retdict = translate_dict(ldict, [('uid', 'username'), \
                           ('commonName', 'commonname'), \
                           ('givenName', 'firstname'), \
                           ('sn', 'lastname'), \
                           ('mail', 'email'), \
                           ('telephoneNumber', 'telephoneNumber'), \
                           ('homePhone', 'homephone'), \
                           ('physicalDeliveryOfficeName', 'physicalDeliveryOfficeName'), \
                           ('title', 'title'), \
                           ('destinationIndicator', 'dept'), \
                           ('description', 'areaOfInterest'), \
                           ('postalAddress', 'address'), \
                           ('businessCategory', 'institute'), \
                           ('registeredAddress', 'supervisor'), \
                           ('carLicense', 'country'), \
                            ])
    return retdict

def loadMadasUser(username):
    'takes a username, returns a dictionary of results'
    'returns empty dict if the user doesnt exist'
    
    user = getMadasUser(username)
    user.refresh()
    details = user.CachedDetails

    if len(details) == 0:
        return {}
    
    #copy one field to a new name
    details['originalEmail'] = details['email']

    #groups
    nodes = user.Nodes
    if len(nodes) > 0:
        details['node'] = user.Nodes[0]
    else:
        details['node'] = []
    details['isAdmin'] = user.IsAdmin
    details['isNodeRep'] = user.IsNodeRep
    details['isClient'] = user.IsClient
    status = user.StatusGroup
    #This is done because the javascript wants 
    #'User' to be seen as 'Active'
    if status == MADAS_USER_GROUP:
        status = 'Active'
    details['status'] = status
    #groups - for some reason the frontend code wants this limited to one?
    #         so I choose the most important.
    if user.IsAdmin:
        details['groups'] = MADAS_ADMIN_GROUP
    elif user.IsNodeRep:
        details['groups'] = MADAS_NODEREP_GROUP
    else:
        details['groups'] = details['node']

    return details  
   
