# Create your views here.

from django.db import models
from django.http import HttpResponse, HttpResponseRedirect
from django.core.urlresolvers import reverse
#from django.core import serializers
#from django.utils import simplejson
from madas.utils import jsonResponse
from django.shortcuts import render_to_response, render_mako
from django.utils.webhelpers import siteurl, wsgibase
import django.utils.webhelpers as webhelpers
from madas.login.views import processLogin
from django.contrib.auth.models import User

def login(request, *args):
    success = processLogin(request, args)
    return HttpResponseRedirect(siteurl(request) + 'repo/') 

def authorize(request, module='/', perms = [], internal = False):
    print '*** authorize : enter ***'

    print 'Subaction: ', request.REQUEST.get('subaction', '')


    #A variable used to determine if we bother using any of the params (session or request)
    #that we see here. Default should be no, unless under specific circumstances
    #namely doing a password reset or viewing a quote from an external link.
    usecachedparams = True 
    cachedparams = None

        #from django.core import serializers
        #json_serializer = serializers.get_serializer("json")()
        #
        #try:
        #    #TODO: This is never going to work. Its not a deserializer.
        #    params = json_serializer.deserialize(params) 
        #except Exception, e:
        #    print '\tException: Could not deserialise params (%s): %s' % (params, str(e))
        #    params = None
    redirectMainContentFunction = request.session.get('redirectMainContentFunction', None)
    if redirectMainContentFunction is not None:
        print '\tUsing session params'
        cachedparams = request.session.get('params', None)
    #else:
        #passing through params of None means the request params are used anyway

    print '\tcachedparams: ', cachedparams


    #check if the session is still valid. If not, log the user out.
    loggedin = request.session.get('loggedin', False)
    if not loggedin:
        if not request.user.is_anonymous():
            request.user.logout() #session gets flushed here
            request.session.flush()
        else:
            #print request.session.__dict__
            if redirectMainContentFunction is not None and\
               redirectMainContentFunction != 'login:resetpassword':
                request.session.flush()

    request.session['params'] = cachedparams
    request.session['redirectMainContentFunction'] = redirectMainContentFunction

    print '\tmodule: %s, perms: %s, internal: %s, basepath: %s' % (str(module), str(perms), str(internal), str(wsgibase()))
    #Check the current user status
    authenticated = request.user.is_authenticated()   
    print '\tuser.is_authenticated was: ', authenticated
  
    #If they are authenticated, make sure they have their groups cached in the session
    if authenticated:
        import utils
        cachedgroups = utils.getGroupsForSession(request)
 
    #here we check the module and the permissions
    authorized = True
    if len(perms) > 0:
        authorized = False
        cachedgroups = request.session.get('cachedgroups', [])
        for perm in perms:
            if perm in cachedgroups:
                authorized = True
 
        if not authorized:        
            print '\tAuthorization failure: %s does not in any of %s' % (request.user.username, perms)
        

    print '\tuser authorized? : ', authorized

    if not authorized:
        destination = 'notauthorized'
    else:
        destination = module 
        print '\tauthorize: destination was ', destination
        
        s = request.REQUEST.get('subaction', '')
        print '\tsubaction was "%s"' % (s)        
        #we want to take them to the login page, UNLESS the destination:subaction was 
        #quote:request or login:forgotpassword or login:<nothing>
        if not authenticated:
            #if not internal and
            if ( destination != 'quote' and s != 'request' and\
                 destination != 'login' and s != 'resetpassword' and\
                 destination != 'login' and s != 'forgotpassword'):
                print '\tDestination is now login'
                destination = 'login'
            else:
                usecachedparams = True
                if s is not None and s != '':
                    destination +=  ':' + s
        else:
            if s is not None and str(s) != '':
                #Append the subaction
                destination += ':' + str(s)
  
        #despite all that, respect the redirectMainContentFunction if is is not None
        #TODO: This is a bit of a hack - we do this here so that we don't wreck
        #the /viewquote?id=1234 functionality. Really, it would be better to have a
        #cleaner way of doing it without having to explicitly check for the
        #redirectMainControlFunction here in authorise, but for the moment this works.
        if redirectMainContentFunction is not None:
            if redirectMainContentFunction == 'login:resetpassword':
                print '\tUsing redirectMainContentFunction because it was login:resetpassword'
                destination = redirectMainContentFunction
                request.session['redirectMainContentFunction'] = None

        print '\tDestination is now "%s"' % (destination)


    if usecachedparams:
        params = cachedparams 
    else:
        params = None

    if authenticated or destination.startswith('login') or destination == 'quote:request':
        if destination == 'login':
            print 'destination was login, so we are setting our request vars'
        setRequestVars(request, success=True, authenticated=authenticated, authorized=authorized, mainContentFunction=destination, params=params) 
    if destination == 'dashboard':
        request.session['redirectMainContentFunction'] = None
        request.session['params'] = None
    
    #We only need to be 'authorized' to be allowed to render the page.
    #if authenticated and authorized:
    if authorized:
        aa = True
    else:
        aa = False

    print '*** authorize : exit ***'
    if not internal:
        return jsonResponse() 
    else:
        return (aa, jsonResponse() )  

from django.template import Context, loader

def redirectMain(request, *args, **kwargs):
    #If we have 'params' in the kwargs, we want to store them in the session.
    #We will want to retrieve them on the other side of the redirect, which
    #will probably be the login function.
   
    if kwargs.has_key('module'):
        red_str = kwargs['module']
        if kwargs.has_key('submodule'):
            red_str += ':%s' % (kwargs['submodule'])

        print 'Setting session[redirectMainContentFunction] to %s' % (red_str)
        request.session['redirectMainContentFunction'] = red_str 
    
    if kwargs.has_key('params'):
        request.session['params'] = kwargs['params']    
        request.session['params'].insert(0, red_str)
        print "Params: " + str(request.session['params'])

    site = siteurl(request)
    if '/repo' in request.META['PATH_INFO']:
        site += 'repo/'

    print 'redirectMain is redirecting to ', site
    return HttpResponseRedirect(site)

    
def serveIndex(request, *args, **kwargs):
    for k in kwargs:
        print '%s : %s' % (k, kwargs[k])
    #so the 'cruft' key will contain a string.
    #we can split this string into 'module/submodule', and have a querystring for good measure
    #we put it in the 'params', and let the login page interpret it.
    if kwargs.has_key('cruft'):
        import re
        #m = re.match(r'(\w+)\/(\w+)?\?(.*)?', kwargs['cruft'])
        m = re.match(r'(\w+)\/(\w+)?', kwargs['cruft'])
        if m is not None:
            fullstring = m.group(0)
            modname = m.group(1)
            funcname = m.group(2)
            qsargs = request.META['QUERY_STRING']
            #for k in request.__dict__['META'].keys():
            #    print '%s : %s ' % (k, request.__dict__['META'][k])

            #parse the qs args
            argsdict = {}
            qsargs = qsargs.strip('?') 
            vars = qsargs.split('&')
            for var in vars:
                if len(var.split('=')) > 1:
                    (key,val) = var.split('=')
                    if key is not None and val is not None:
                        argsdict[key] = val


            from utils import param_remap
            argsdict = param_remap(argsdict)

            print 'module: %s, funcname %s, argsdict %s' % (modname, funcname, argsdict)
        #else:
        #    print 'No match'

            params = [argsdict]
            print 'redirecting'
            return redirectMain(request, module = modname, submodule = funcname, params = params)
        else:
            params = request.session.get('params', [])

    #get or create the user
    user, created = User.objects.get_or_create(username=request.user.username)
    if created is True:
        user.save()

    #print 'serve index...' 
    #print settings.APP_SECURE_URL
    #print request.username
    #print request.session.get('mainContentFunction', '')
    request.params = params
    from django.utils import simplejson
    m = simplejson.JSONEncoder()
    paramstr = m.encode(params)
    return render_mako('repo_index.mako', 
                        APP_SECURE_URL = siteurl(request),#settings.APP_SECURE_URL,
                        username = request.user.username,
                        mainContentFunction = request.session.get('mainContentFunction', 'dashboard'),
                        wh = webhelpers,
                        params = '' # params[1] #None #['quote:viewformal', {'qid': 83}]
                      )

def processLogout(request, *args):
    from django.contrib.auth import logout
    print '*** processLogout : enter***'
    print '\tlogging out (django)'
    logout(request) #let Django log the user out
    setRequestVars(request, success=True, mainContentFunction = 'login')
    print '*** processLogout : exit***'
    return jsonResponse()

def serverinfo(request):
    return render_mako('serverinfo.mako', s=settings, request=request, g=globals() )

