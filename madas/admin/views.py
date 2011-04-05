# Create your views here.
from django.db import models
from django.http import HttpResponse, HttpResponseNotFound
from django.contrib.auth.ldap_helper import LDAPHandler
from django.contrib.auth.models import User

from madas.utils.data_utils import jsonResponse, json_encode, translate_dict
from madas.quote.models import Quoterequest, Formalquote, Organisation, UserOrganisation
from django.db.models import Q
from madas.repository.json_util import makeJsonFriendly
from django.utils import simplejson as json

from django.conf import settings
from settings import MADAS_STATUS_GROUPS, MADAS_ADMIN_GROUPS
from django.contrib.auth.decorators import login_required
from madas.decorators import admins_only, admins_or_nodereps
from madas.users.MAUser import getCurrentUser

@admins_or_nodereps
def admin_requests(request, *args):
    '''This corresponds to Madas Dashboard->Admin->Active Requests
       Accessible by Administrators, Node Reps
    '''
    print '***admin requests : enter***'
    print 'admin_requests'
    #provide livegrid pager data for admin requests
    searchgroup = []

    g = getCurrentUser(request).CachedGroups 
    if 'Administrators' not in g and 'Node Reps' in g:
        from madas.users import views
        searchgroup = views.getNodeMemberships(g)
    searchgroup.append('Pending')
    
    print 'Searchgroup was: ', searchgroup    
    
    ld = LDAPHandler() 
    ul = ld.ldap_list_users(searchgroup)
   
    #now do our keyname substitution
    newlist = []
    try:
        for entry in ul:
            d = translate_dict(entry, [\
                           ('uid', 'username'), \
                           ('commonName', 'commonname'), \
                           ('givenName', 'firstname'), \
                           ('sn', 'lastname'), \
                           ('mail', 'email'), \
                           ('telephoneNumber', 'telephoneNumber'), \
                           ('homephone', 'homephone'), \
                           ('physicalDeliveryOfficeName', 'physicalDeliveryOfficeName'), \
                           ('title', 'title'), \
                                ]) 
            newlist.append(d)
    except Exception, e:
        print 'admin_requests: Exception: ', str(e)   

    print '***admin requests : exit***'

    return jsonResponse(items=newlist)  

@admins_or_nodereps
def user_search(request, *args):
    '''This corresponds to Madas Dashboard->Admin->Active User Search
       Accessible by Administrators, Node Reps
    '''
    g = getCurrentUser(request).CachedGroups 
    searchGroup = []
    
    if 'Administrators' not in g and 'Node Reps' in g:
        from madas.users import views
        searchGroup = views.getNodeMemberships(g)
    
    #no matter what, include Active users in the group. 
    searchGroup.append('User')

    ld = LDAPHandler()
    
    ul = ld.ldap_list_users(searchGroup)
    
    #print 'UL', ul

    #now do our keyname substitution
    newlist = []
    try:
        for entry in ul:
            from madas.users.views import _userload
            d = translate_dict(entry, [\
                           ('uid', 'username'), \
                           ('commonName', 'commonname'), \
                           ('givenName', 'firstname'), \
                           ('sn', 'lastname'), \
                           ('mail', 'email'), \
                           ('telephoneNumber', 'telephoneNumber'), \
                           ('homephone', 'homephone'), \
                           ('physicalDeliveryOfficeName', 'physicalDeliveryOfficeName'), \
                           ('title', 'title'), \
                                ])
            
            #f = _userload(entry['uid'][0])
            #if len(f) > 0:
            #    d['isClient'] = f['isClient']
            #else:
            #    d['isClient'] = False
            
            #Rather than do an expensive _userload for every user to determine
            #if they are a client or not, we just test here to see if the 
            #only group they are in is a status group. If so, they are a client.
            #This is for performance - this was timing out on my local client.
            
            d['isClient'] = False
            if entry.has_key('groups'):
                e = entry['groups']
                if len(e) == 1 and e[0] in settings.MADAS_STATUS_GROUPS:
                    d['isClient'] = True

            newlist.append(d)
    except Exception, e:
        print json_encode(e)   



    return jsonResponse(items=newlist) 

@admins_or_nodereps
def rejected_user_search(request, *args):
    '''This corresponds to Madas Dashboard->Admin->Rejected User Search
       Accessible by Administrators, Node Reps
    '''
    print '***rejected_user_search : enter ***' 
    ld = LDAPHandler()
    searchgroup = []
   
    g = getCurrentUser(request).CachedGroups 
    
    if 'Administrators' not in g and 'Node Reps' in g:
        from madas.users import views
        searchgroup = views.getNodeMemberships(g)
    searchgroup.append('Rejected') #What about if this is already in there?

    print '\tsearch group was ', searchgroup
    ld = LDAPHandler()
    ul = ld.ldap_list_users(searchgroup)
    
    #print 'UL', ul

    #now do our keyname substitution
    newlist = []
    try:
        for entry in ul:
            d = translate_dict(entry, [\
                           ('uid', 'username'), \
                           ('commonName', 'commonname'), \
                           ('givenName', 'firstname'), \
                           ('sn', 'lastname'), \
                           ('mail', 'email'), \
                           ('telephoneNumber', 'telephoneNumber'), \
                           ('homephone', 'homephone'), \
                           ('physicalDeliveryOfficeName', 'physicalDeliveryOfficeName'), \
                           ('title', 'title'), \
                                ]) 
            newlist.append(d)
    except Exception, e:
        print '\tEXCEPTION: ', str(e)
    print '***rejected_user_search : exit ***' 
    return jsonResponse(items=newlist) 

@admins_or_nodereps
def deleted_user_search(request, *args):
    '''This corresponds to Madas Dashboard->Admin->Deleted User Search
       Accessible by Administrators, Node Reps
    '''
    print '***deleted_user_search : enter ***' 
    g = getCurrentUser(request).CachedGroups 
    searchgroup = [] 
    if 'Administrators' not in g and 'Node Reps' in g:
        from madas.users import views
        searchgroup = views.getNodeMemberships(g)
    searchgroup.append('Deleted') #What about if this is already in there?

    print '\tsearch group was ', searchgroup
    ld = LDAPHandler()
    ul = ld.ldap_list_users(searchgroup)
   
    #now do our keyname substitution
    newlist = []
    try:
        for entry in ul:
            d = translate_dict(entry, [\
                           ('uid', 'username'), \
                           ('commonName', 'commonname'), \
                           ('givenName', 'firstname'), \
                           ('sn', 'lastname'), \
                           ('mail', 'email'), \
                           ('telephoneNumber', 'telephoneNumber'), \
                           ('homephone', 'homephone'), \
                           ('physicalDeliveryOfficeName', 'physicalDeliveryOfficeName'), \
                           ('title', 'title'), \
                                ])
            newlist.append(d)
    except Exception, e:
        print str(e)
    print '\tNewList: ', newlist
    print '***deleted_user_search : exit ***' 
    return jsonResponse(items=newlist) 

@admins_or_nodereps
def user_load(request, *args):
    '''This is called when an admin user opens up an individual user record
       from an admin view e.g. Active User Search
       Accessible by Administrators, Node Reps
    '''
    print '***admin/user_load : enter ***' 
    import madas.users 
    from madas.users.views import _userload
    print '\tloading user'
    d = _userload(request.REQUEST['username'])
    print '\tfinished loading user'
    
    #find user organisation
    try:
        u = User.objects.get(username=request.REQUEST['username'])
        orgs = UserOrganisation.objects.filter(user=u)
        d['organisation'] = ''
        if len(orgs) > 0:
            d['organisation'] = orgs[0].organisation.id
            print 'user in org %d' % (orgs[0].organisation.id)
    except Exception, e:
        print 'Exception ', str(e)
        pass

    print '***admin/user_load : exit ***' 
    return jsonResponse(data=d)

@admins_or_nodereps
def user_save(request, *args):
    '''This is called when an admin user hits save on an individual user record
       from an admin view e.g. Active User Search
       Accessible by Administrators, Node Reps
    '''
    print '***admin/user_save : enter ***' 
    import madas.users 
    from madas.users.views import _usersave
    oldstatus, status =  _usersave(request, request.REQUEST['email'], admin=True)

    #oldstatus is a list. Even though people should only have one status, if there
    #is ever an error state where they do somehow end up in two states (or 0) it is easier
    #to leave oldstatus as a list and use a foreach than it is to test lengths and do a bunch
    #of dereferencing. By rights, oldstatus should only contain one element though.
    if status not in oldstatus:
        print '\toldstatus (%s) was not equal to status (%s)' % (oldstatus, status)
        from mail_functions import sendApprovedRejectedEmail, sendAccountModificationEmail
        if status == 'User':
            status = 'Approved' #transform status name
        if status == 'Approved' or status == 'Rejected':
            sendApprovedRejectedEmail(request, request.REQUEST['email'], status)
        else:
            sendAccountModificationEmail(request, request.REQUEST['email'])
        

    #do something based on 'status' (either '' or something new)
    nextview = 'admin:usersearch'
    if status != '':
        if status == 'Pending':
            nextview = 'admin:adminrequests'
        elif status == 'Rejected':
            nextview = 'admin:rejectedUsersearch'
        elif status == 'Deleted':
            nextview = 'admin:deletedUsersearch'

    #apply organisational changes
    try:
        targetUser = User.objects.get(username=request.REQUEST['email'])
    except:
        targetUser = User.objects.create_user(request.REQUEST['email'], request.REQUEST['email'], '')
        targetUser.save()
        
    try:
        UserOrganisation.objects.filter(user=targetUser).delete()

        org = Organisation.objects.get(id=request.REQUEST['organisation'])
    
        if org:
            uo = UserOrganisation(user=targetUser, organisation=org)
            uo.save()
            print 'added user to org'
    except:
        print 'FATAL error adding or removing user from organisation'

    print '***admin/user_save : exit ***' 

    return jsonResponse(mainContentFunction=nextview) 

@admins_or_nodereps
def node_save(request, *args):
    '''This is called when saving node details in the Node Management.
       Madas Dashboard->Admin->Node Management
       Accessible by Administrators, Node Reps
    '''
    print '*** node_save : enter ***'
    oldname = str(request.REQUEST.get('originalName', ''))
    newname = str(request.REQUEST.get('name', ''))
    print '\toriginal name was: ', oldname 
    print '\tnew name is: ', newname
   
    returnval = False 
    if oldname!=newname and newname !='':
        if oldname == '':
            #new group
            #Group creation/renaming requires an admin auth to ldap.
            ld = LDAPHandler(userdn=settings.LDAPADMINUSERNAME, password=settings.LDAPADMINPASSWORD)
            returnval = ld.ldap_add_group(newname)
        else:
            #rename
            #Group creation/renaming requires an admin auth to ldap.
            ld = LDAPHandler(userdn=settings.LDAPADMINUSERNAME, password=settings.LDAPADMINPASSWORD)
            returnval = ld.ldap_rename_group(oldname, newname)
    print '\tnode_save: returnval was ', returnval      
    #TODO: the javascript doesnt do anything if returnval is false...it just looks like nothing happens.
    print '*** node_save : exit ***'
    return jsonResponse(success=returnval, mainContentFunction='admin:nodelist') 

@admins_or_nodereps
def node_delete(request, *args):
    '''This is called when saving node details in the Node Management.
       Madas Dashboard->Admin->Node Management
       Accessible by Administrators, Node Reps
    '''
    print '*** node_delete : enter ***'
    #We must make sure 'Administrator' and 'User' groups cannot be deleted.
    delname = str(request.REQUEST.get('name', ''))
    ldelname = delname.lower()
    if ldelname == 'administrators' or ldelname == 'users':
        #Don't delete these sorts of groups.
        pass
    else:
        #Group creation/renaming requires an admin auth to ldap.
        ld = LDAPHandler(userdn=settings.LDAPADMINUSERNAME, password=settings.LDAPADMINPASSWORD)
        ret = ld.ldap_delete_group(delname)

    print '*** node_delete : enter ***'
    return jsonResponse(mainContentFunction='admin:nodelist') 

@admins_or_nodereps
def org_save(request):

    args = request.REQUEST

    org_id = args['id']

    if org_id == '0':
        org = Organisation()
    else:
        org = Organisation.objects.get(id=org_id)
        
    org.name = args['name']
    org.abn = args['abn']
    
    org.save()
        
    return jsonResponse()
    
@admins_or_nodereps
def org_delete(request):

    args = request.REQUEST
    org_id = args['id']

    rows = Organisation.objects.filter(id=org_id)
    rows.delete()

    return jsonResponse()

@admins_or_nodereps
def list_organisations(request):

    if request.GET:
        args = request.GET
    else:
        args = request.POST
       

    # basic json that we will fill in
    output = {'metaData': { 'totalProperty': 'results',
                            'successProperty': 'success',
                            'root': 'rows',
                            'id': 'id',
                            'fields': [{'name':'id'}, {'name':'name'}, {'name':'abn'}]
                            },
              'results': 0,
              'authenticated': True,
              'authorized': True,
              'success': True,
              'rows': []
              }

    authenticated = request.user.is_authenticated()
    authorized = True # need to change this
    if not authenticated or not authorized:
        return HttpResponse(json.dumps(output), status=401)


    rows = Organisation.objects.all() 

    # add row count
    output['results'] = len(rows);

    # add rows
    for row in rows:
        d = {}
        d['id'] = row.id
        d['name'] = row.name
        d['abn'] = row.abn

        output['rows'].append(d)


    output = makeJsonFriendly(output)

    return HttpResponse(json.dumps(output))
