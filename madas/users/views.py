# Create your views here.
from django.contrib.auth.ldap_helper import LDAPHandler
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseRedirect
from django.utils import simplejson
from madas.users.MAUser import *
from madas.users.MAUser import _translate_ldap_to_madas, _translate_madas_to_ldap 
from madas.utils.data_utils import jsonResponse, makeJsonFriendly
from madas.utils.mail_functions import sendAccountModificationEmail

##The user info view, which sends the state of the logged in
##user to the frontend.
def userinfo(request):
    m = getCurrentUser(request)
    m.refresh()
    return HttpResponse(m.toJson())


def listAllNodes(request, *args):
    '''
    This view lists all nodes in the system
    These are the groups left over when the
    status and administrative groups are removed
    
    The format for the return is a list of dicts,
    each entry having a 'name' and a 'submitvalue'

    Note: this is for use in a dropdown which expects
    an additional option "Don't Know" which has the value ''. 
    If request.REQUEST has 'ignoreNone', we do not do this.
    "" 
    '''
    ldapgroups = getMadasGroups()
    groups = []
    if not request.REQUEST.has_key('ignoreNone'):
        groups.append({'name':'Don\'t Know', 'submitValue':''})

    for groupname in ldapgroups:
        #Cull out the admin groups and the status groups
        if groupname not in MADAS_STATUS_GROUPS and groupname not in MADAS_ADMIN_GROUPS:
            groups.append({'name':groupname, 'submitValue':groupname})
    return jsonResponse(items=groups)

    

#Use view decorator here
@login_required
def userload(request, *args):
    '''This is called when loading user details - when the user
       clicks on the User button in the dashboard and selects 'My Account'
       Accessible by any logged in user
    '''
    logger.debug('***userload : enter ***')
    u = request.REQUEST.get('username', request.user.username)
    d = [loadMadasUser(u)]
    d = makeJsonFriendly(d)
    logger.debug('***userload : exit ***') 
    return jsonResponse(data=d)   

def _usersave(request, username, admin=False):
    ''' Saves user details, from a form.
    Uses the form details from the request, but and the supplied username.
    If this is an admin save (i.e. the user is not necessarily updating
    their own record), then pass admin = True, so that an admin level LDAP
    connection can be made.'''
    r = request.REQUEST
    u = username
    currentuser = getCurrentUser(request)

    originalEmail = str(u)
    username = str(r.get('email', originalEmail)) #if empty, set to originalEmail
    email = str(r.get('email', originalEmail)) #if empty, set to originalEmail
    password = (str(r.get('password',  ''))).strip() #empty password will be ignored anyway.
    firstname = str(r.get('firstname', ''))
    lastname = str(r.get('lastname', ''))
    telephoneNumber = str(r.get('telephoneNumber', ''))
    homephone = str(r.get('homephone', ''))
    physicalDeliveryOfficeName = str(r.get('physicalDeliveryOfficeName', ''))
    title = str(r.get('title', '' ))
    dept = str(r.get('dept', ''))
    institute = str(r.get('institute', ''))
    address= str(r.get('address', ''))
    supervisor = str(r.get('supervisor', ''))
    areaOfInterest = str(r.get('areaOfInterest', ''))
    country = str(r.get('country', ''))
    
    isAdmin = r.get('isAdmin')
    isNodeRep = r.get('isNodeRep')
    node = str(r.get('node'))
    status = str(r.get('status', None))

    if status == 'Active':
        status = 'User'


    updateDict = {} #A dictionary to hold name value pairs of attrubutes to pass to LDAP to update.
                    #The name fields must match the ldap schema - no translation is done by the 
                    #LDAP module.

    updateDict['mail'] = email
    updateDict['telephoneNumber'] = telephoneNumber 
    updateDict['physicalDeliveryOfficeName'] = physicalDeliveryOfficeName
    updateDict['title'] = title
    updateDict['cn'] = "%s %s" % (firstname, lastname)
    updateDict['givenName'] = firstname
    updateDict['sn'] = lastname
    updateDict['homePhone'] = homephone
    updateDict['postalAddress'] = address
    updateDict['description'] = areaOfInterest
    updateDict['destinationIndicator'] = dept
    updateDict['businessCategory'] = institute
    updateDict['registeredAddress'] = supervisor
    updateDict['carlicense'] = country
   
   
    #Any fields that were passed through as empty should be refilled with their old values, if possible
    #i.e. if the user existed.
    previous_details = loadMadasUser(u)
    previous_details = _translate_madas_to_ldap(previous_details)
    
    #print 'Previous: '
    #print previous_details
    for field in updateDict.keys():
        if updateDict[field] == '':
            print 'Empty field. Replacing with previous value: \'',previous_details.get(field, ''), '\'' 
            updateDict[field] = previous_details.get(field, '')

    import utils
    groups = getMadasUserGroups(u, False)
    oldstatus = []
    #sanitise the format of 'groups' - we dont want the statuses.
    if len(groups) > 0:
        #get status info first
        if len(groups['status']) > 0:
            oldstatus = groups['status']
        else:
            oldstatus = []
        #then make groups just the groups part
        groups = groups['groups']
    else:
        groups = []
    oldnodes = getMadasNodeMemberships(groups)
    oldnode = []
    if len(oldnodes) > 0:
        oldnode = [oldnodes[0]] #only allow one 'oldnode'
    else:
        oldnode = []

    print 'Groups is: ', groups
    print 'Nodes is: ', oldnode
    print 'User Groups is: ', getMadasUserGroups(u, False)
    print 'Node is ', node

    #don't let a non-admin change their node
    if currentuser.IsAdmin and admin:
        #TODO do something with the new status
        if node != '': #empty string is 'Don't Know' 
            newnode = [node] #only allow one 'newnode'
            print 'Got new node %s and was admin' % (node)
        else:
            newnode = []
    else:
        #TODO use the old status, don't capture whatever was POSTed.
        newnode = oldnode

    #We dont actually permit the user to modify their email address at the moment for security purposes.
    #Get an admin connection to LDAP
    ld = LDAPHandler(userdn=settings.LDAPADMINUSERNAME, password=settings.LDAPADMINPASSWORD)
    r = None
    try:
        if previous_details == {}: #the user didnt exist
            #objclasses = ['top', 'inetOrgPerson', 'simpleSecurityObject', 'organizationalPerson', 'person']
            objclasses = 'inetorgperson'
            worked = ld.ldap_add_user(username, updateDict, objectclasses=objclasses, usercontainer='ou=NEMA', userdn='ou=People', basedn='dc=ccg,dc=murdoch,dc=edu,dc=au')
            ld.ldap_add_user_to_group(username, 'Pending')
            if not worked:
                raise Exception, 'Could not add user %s' % (username)
        else:
            r = ld.ldap_update_user(u, username, password, updateDict, pwencoding='md5')
        print '\tUser update successful for %s' % (u) 
    except Exception, e:
        print '\tException when updating user %s: %s' % (u, str(e))
   
    #only trust the isAdmin checkbox if editing user is an admin
    if currentuser.IsAdmin and admin:
        #honour 'isAdmin' checkbox
        if isAdmin is not None:
            if isAdmin:
                print 'isAdmin was True!'
                # add the user to the administrators group - but not if they are already there.
                ld.ldap_add_user_to_group(username, 'Administrators')
            else:
                print 'isAdmin was False!'
                #only remove from admin group if logged in name doesnt match name of user being updated.
                #i.e. don't let an admin user un-admin themselves
                if request.user.username != username:
                    ld.ldap_remove_user_from_group(username, 'Administrators')
        else:
            print 'isAdmin was False!'
            #only remove from admin group if logged in name doesnt match name of user being updated.
            #i.e. don't let an admin user un-admin themselves
            if request.user.username != username:
                ld.ldap_remove_user_from_group(username, 'Administrators')
        
        print '\tperforming node updates for ', username
        print '\tnewnode: ', newnode
        print '\toldnode: ', oldnode
        #update to new nodes
        for nn in newnode:
            if nn not in oldnode:
                print '\tAdding %s to group: %s' % (username, nn)
                ld.ldap_add_user_to_group(username, nn)
        
        for on in oldnodes: #note this is oldnodes, not oldnode. So this is the original list.
            if on not in newnode:
                #remove from any incorrect nodes:
                print '\tRemoving %s from group: %s' % (username, on)
                ld.ldap_remove_user_from_group(username, on)

    else: #user wasnt an admin
        print 'Non admin user. No node updates performed'

    if admin and (currentuser.IsAdmin or currentuser.IsNodeRep):
        #honour 'isNodeRep' checkbox
        if isNodeRep is not None:
            if isNodeRep: 
                print 'isNodeRep was True!'
                #add to node reps group
                ld.ldap_add_user_to_group(username, 'Node Reps')
            else:
                print 'isNodeRep was False!'
                #remove from node reps group
                ld.ldap_remove_user_from_group(username, 'Node Reps')
        else:
            print 'isNodeRep was False!'
            #remove from node reps group
            #i.e. don't let a noderep user un-admin themselves
            if request.user.username != username:
                ld.ldap_remove_user_from_group(username, 'Node Reps')

        
        #do status changes
        if status is not None:
            #be careful not to remove the user from all groups - this is a real pain to correct.
            #instead, add them to a group first, and only do the remove if the add succeeds.

            print '\tAdding %s to group %s' % (username, status)
            if ld.ldap_add_user_to_group(username, status):
                for old_st in oldstatus:
                    if old_st != status: #don't remove them from the group we just added them to
                        print '\tRemoving %s from group: %s' % (username, old_st)
                        ld.ldap_remove_user_from_group(username, old_st)
            else:
                print '\tWARNING: Could not add %s to %s, so removal from %s was not done.' % (username, status, oldstatus)
            
    else:
        print 'Non admin/node-rep user. No Status updates performed.'

    #force a new lookup of the users' groups to be cached, in case the modified user is the logged in user.
    currentuser = getCurrentUser(request, force_refresh=True) 

    if status is None or not currentuser.IsAdmin:
        return oldstatus, oldstatus
    else:
        return oldstatus, status

def userSave(request, *args):
    '''This is called when saving user details - when the user
       clicks on the User button in the dashboard and selects 'My Account',
       changes some details, and hits 'save'
       Accessible by any logged in user
    '''
    logger.debug('***users/userSave : enter ***' )

    u = request.user.username
    returnval = _usersave(request,u)

    sendAccountModificationEmail(request, u)

    logger.debug('***users/userSave : exit ***') 
    return jsonResponse(mainContentFunction='user:myaccount')





