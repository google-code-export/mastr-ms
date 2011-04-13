import datetime
import os
import zipfile
from decimal import Decimal
from django.core.serializers.json import DateTimeAwareJSONEncoder
from django.db.models import Model
from django.db.models.query import QuerySet
from django.utils import simplejson as json
from django.http import HttpResponse
from django.db.models import Model

from django.utils import simplejson
from django.utils.functional import Promise
from django.utils.translation import force_unicode
from django.utils.encoding import smart_unicode
from django.core.serializers.json import DjangoJSONEncoder

from django.contrib.auth.ldap_helper import LDAPHandler


def makeJsonFriendly(data):
    '''Will traverse a dict or list compound data struct and
       make any datetime.datetime fields json friendly
    '''
    #print 'makeJsonFriendly called with data: ', str(data)
    #print 'which was a ', type(data)
    try:
        if isinstance(data, list):
            #print 'handling list'
            for e in data:
                e = makeJsonFriendly(e)
        elif isinstance(data, dict):
            #print 'handling dict'
            for key in data.keys():
                data[key] = makeJsonFriendly(data[key])
            
        elif isinstance(data, datetime.datetime):
            #print 'handling datetime'
            #print 'converting datetime: ', str(data)
            return data.strftime('%Y/%m/%d %H:%M')
        else:
            #print 'handling default case. Type was ', type(data)
            #print 'returning unmodified'
            return data #unmodified
    except Exception, e:
        print 'makeJsonFriendly encountered an error: ', str(e)
    #print 'end makeJsonFriendly'    
    return data

# ------------------------------------------------------------------------------
class ModelJSONEncoder(DjangoJSONEncoder):
    """
    (simplejson) DjangoJSONEncoder subclass that knows how to encode fields.y/

    (adated from django.serializers, which, strangely, didn't
     factor out this part of the algorithm)
    """
    def handle_field(self, obj, field):
        return smart_unicode(getattr(obj, field.name), strings_only=True)
    
    def handle_fk_field(self, obj, field):
        related = getattr(obj, field.name)
        if related is not None:
            if field.rel.field_name == related._meta.pk.name:
                # Related to remote object via primary key
                related = related._get_pk_val()
            else:
                # Related to remote object via other field
                related = getattr(related, field.rel.field_name)
        return smart_unicode(related, strings_only=True)
    
    def handle_m2m_field(self, obj, field):
        if field.creates_table:
            return [
                smart_unicode(related._get_pk_val(), strings_only=True)
                for related
                in getattr(obj, field.name).iterator()
                ]
    
    def handle_model(self, obj):
        dic = {}
        for field in obj._meta.local_fields:
            if field.serialize:
                if field.rel is None:
                    dic[field.name] = self.handle_field(obj, field)
                else:
                    dic[field.name] = self.handle_fk_field(obj, field)
        for field in obj._meta.many_to_many:
            if field.serialize:
                dic[field.name] = self.handle_m2m_field(obj, field)
        return dic
    
    def default(self, obj):
        if isinstance(obj, Model):
            return self.handle_model(obj)
        else:
            return super(ModelJSONEncoder, self).default(obj)

# ------------------------------------------------------------------------------
class LazyEncoder(ModelJSONEncoder):
    def default(self, o):
        if isinstance(o, Promise):
            return force_unicode(o)
        else:
            return super(LazyEncoder, self).default(o)


def json_encode(data):
    m = ModelJSONEncoder()
    try:
        d = m.encode(data)
        return d
    except Exception, e:
        print 'json_encode: couldn\'t encode', data, ':', str(e)
        return None

def json_decode(data):
    try:
        m = simplejson.JSONDecoder()
        d = m.decode(data)
        return d
    except Exception, e:
        print 'json_decode: couldn\'t decode ', data, ':', str(e)
        return data



def uniqueList(l):
    '''returns unique elements of l.
       sometimes you can use a set to do this, but 
       not if your list contains unhashable types, such as dict.
    '''
 
    seen = []
    result = []
    for i in l:
        if i not in seen:
            result.append(i)
        seen.append(i)

    return result


#def getGroupsForSession(request, force_reload = False):
#    cachedgroups = request.session.get('cachedgroups', [])
#    if cachedgroups is [] or force_reload:
#        print '\tNo cached groups for %s. Fetching.' % (request.user.username)
#        ld = LDAPHandler()
#        g = ld.ldap_get_user_groups(request.user.username)
#        request.session['cachedgroups'] = g
#        print '\tStored groups for %s: %s' % (request.user.username, request.session.get('cachedgroups') )
#        cachedgroups = g
#        
#        request.session['isNodeRep'] = False
#        request.session['isAdmin'] = False
#
#        if cachedgroups:
#            request.session['isClient'] = False
#        
#            for group in cachedgroups:
#                if group == 'Administrators':
#                    request.session['isAdmin'] = True
#                if group == 'Node Reps':
#                    request.session['isNodeRep'] = True
#        
#            if len(cachedgroups) == 1 and cachedgroups[0] == 'User':        
#                request.session['isClient'] = True
#                print 'isClient'
#
#    return cachedgroups


#def setRequestVars(request, success=False, authenticated = 0, authorized = 0, totalRows = 0, user={}, mainContentFunction = '', username='', params = None, items=None, data=None):
#    """Make sure we set the session vars the same way each time, with sensible defaults"""
#    
#    if params is None:
#        p = request.REQUEST.get('params', None)
#        if p is not None:
#            p = json_decode(p)
#            print '\tSet Request Vars decoded params as : ', p
#        params = p
#    
#    print '\tSet Request Vars params are ', params
#
#    store = {}
#    store['success']              = success
#    store['authenticated']        = authenticated
#    store['authorized']           = authorized
#    store['totalRows']            = totalRows
#    store['mainContentFunction']  = mainContentFunction
#    store['params']               = params
#    store['user']                 = user
#    #print 'Setting params. ', params, 'Type was: ', type(request.store['params'])
#    if items is None:
#        store['items']            = items
#    else:
#        store['items']            = list(items)
#    #print 'setSessionVars, mainContentFunction is: ', request.store['mainContentFunction'] 
#    
#    if data is not None:
#        store['data'] = data
#
#    #set the store on the session
#    request.session['store'] = store

def get_var(dictionary, key, defaultvalue):
    if dictionary.has_key(key):
        v = dictionary[key]
        #if type(v) is list and len(v) ==1:
        #    v = v[0] 
        return v 
    else:
        return defaultvalue

def translate_dict(data, tuplelist, includeRest = False):
    """takes data (should be a dict) and tuple list (list of tuples)
       for each tuple in the list, if the key (element 1) exists in the dict
       then its value is associated with a new key (element 2) in a new
       dict, which is returned.
       if 'includeRest' is True, any keys not mentioned are transplanted to 
       the new dict 'as is'
    """
    returnval = {}
    oldkeylist = []
    for oldkey, newkey in tuplelist:
        oldkeylist.append(oldkey)
        val = get_var(data, oldkey, 'KEYNOTFOUND!!')
        if val != 'KEYNOTFOUND!!':
            returnval[newkey] = val
        #otherwise dont bother adding this key, it wasnt in the original data
    if includeRest is True:
        for key in data.keys():
            if key not in oldkeylist:
                returnval[key] = data[key]

    return returnval         


def param_remap(d):
    for key in d:
        if key == 'quoterequestid':
            v = d[key]
            del d[key]
            d['qid'] = v
    return d

def jsonErrorResponse(msg='An error occured'):
    retdata = json.dumps({
        'success': False,
        'msg': msg
    })
    return HttpResponse(retdata)

def jsonResponse(data={}, items=None, mainContentFunction=None, params=None):
    #Sometimes we are passed 'data', and sometimes 'items'. We need to make
    #a decision based on which one we are going to use for the 'totalRows'.
    if items:
        totalrows = len(items)
    else:    
        totalrows = len(data)
    version = 1
    response = {'value': {'items':makeJsonFriendly(items), 'version':1, 'total_count':totalrows}}
    
    retval = {'success': True, 
              'data':makeJsonFriendly(data), 
              'totalRows':totalrows,
              'response': response 
              }
    if params:
        retval['params'] = params
    if mainContentFunction:
        retval['mainContentFunction'] = mainContentFunction

    retdata = json.dumps(retval)
    return HttpResponse(retdata)


def zipdir(dirPath=None, zipFilePath=None, includeDirInZip=True):

    if not zipFilePath:
        zipFilePath = dirPath + ".zip"
    if not os.path.isdir(dirPath):
        raise OSError("dirPath argument must point to a directory. "
            "'%s' does not." % dirPath)
    parentDir, dirToZip = os.path.split(dirPath)
    #Little nested function to prepare the proper archive path
    def trimPath(path):
        archivePath = path.replace(parentDir, "", 1)
        if parentDir:
            archivePath = archivePath.replace(os.path.sep, "", 1)
        if not includeDirInZip:
            archivePath = archivePath.replace(dirToZip + os.path.sep, "", 1)
        return os.path.normcase(archivePath)
    
    outFile = zipfile.ZipFile(zipFilePath, "w", compression=zipfile.ZIP_DEFLATED)
    for (archiveDirPath, dirNames, fileNames) in os.walk(dirPath):
        for fileName in fileNames:
            filePath = os.path.join(archiveDirPath, fileName)
            outFile.write(filePath, trimPath(filePath))
        #Make sure we get empty directories as well
        if not fileNames and not dirNames:
            zipInfo = zipfile.ZipInfo(trimPath(archiveDirPath) + "/")
            #some web sites suggest doing
            #zipInfo.external_attr = 16
            #or
            #zipInfo.external_attr = 48
            #Here to allow for inserting an empty directory.  Still TBD/TODO.
            outFile.writestr(zipInfo, "")
            
    outFile.close()
