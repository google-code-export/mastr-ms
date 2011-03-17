from madas.utils import getGroupsForSession
from django.utils import simplejson

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

    def refresh(self, request):
        #defaults
        self.IsLoggedIn = False
        self.IsAdmin = False
        self.IsClient = False
        self.IsNodeRep = False
        self.Username = ""

        if request.user:
            self.IsLoggedIn = request.user.is_authenticated()
            self.Username = request.user.username
            #Grab groups, forcing a reload. These are stored in the session,
            #along with other variables like IsAdmin etc.
            self.CachedGroups = getGroupsForSession(request, force_reload = True)
            if self.CachedGroups is None:
                self.CachedGroups = [];
            self.IsAdmin = request.session.get('isAdmin', False)
            self.IsNodeRep = request.session.get('isNodeRep', False)
            self.IsClient = request.session.get('isClient', False)
  
        #Store this user in the session
        request.session['mauser'] = self

    def getData(self):
        return self._dict
    def toJson(self):
        return simplejson.dumps(self._dict)
