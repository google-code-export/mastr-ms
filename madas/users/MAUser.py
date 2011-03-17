from django.utils import simplejson
from django.contrib.auth.ldap_helper import LDAPHandler


#Gets the MAUser object out of the session.
def getCurrentUser(request):
    if not request.session.get('mauser', False):
        request.session['mauser'] = MAUser();
        MAUser.refresh();
    return request.session['mauser']

#Just a class to encapsulate data to send to the frontend (as json)
class MAUser(object):
    def __init__(self):
        self._dict = {}
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
        return self._dict.get('CachedGroups', [])
    @CachedGroups.setter
    def CachedGroups(self, value):
        self._dict['CachedGroups'] = value

    def getGroupsForUser(self, force_reload = False):
        if self.CachedGroups is [] or force_reload:
            print '\tNo cached groups for %s. Fetching.' % (self.Username)
            ld = LDAPHandler()
            self.CachedGroups = ld.ldap_get_user_groups(self.Username)
        return self.CachedGroups    
    
    def refresh(self, request):
        #defaults
        self.IsLoggedIn = False
        self.IsAdmin = False
        self.IsClient = False
        self.IsNodeRep = False
        self.IsStaff = False
        self.Username = ""

        if request.user:
            self.IsLoggedIn = request.user.is_authenticated()
            self.Username = request.user.username
            #Grab groups, forcing a reload. These are stored in the session,
            #along with other variables like IsAdmin etc.
            self.CachedGroups = self.getGroupsForUser(force_reload = True)
            if self.CachedGroups is None:
                self.CachedGroups = [];
            
            if 'Administrators' in self.CachedGroups:
                self.IsAdmin = True
            if 'Node Reps' in self.CachedGroups:
                self.IsNodeRep = True
            
            #For 'staff':
            #They are not an admin
            #They are not a NodeRep
            #But they are part of some other group.
            #Note that all users are part of a 'User' group, so the test is:
            #!admin and !noderep and numgroups > 1
            if not self.IsAdmin and not self.IsNodeRep and len(self.CachedGroups) > 1:
                self.IsStaff = True
            elif len(self.CachedGroups) == 1 and 'User' in self.CachedGroups:
                self.IsClient = True

        #Store this user in the session
        request.session['mauser'] = self

    def getData(self):
        return self._dict
    def toJson(self):
        return simplejson.dumps(self._dict)
