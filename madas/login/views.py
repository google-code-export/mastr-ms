# Create your views here.
from django.http import HttpResponse, HttpResponseRedirect
import django.utils.webhelpers
from django.utils.webhelpers import siteurl, wsgibase

from madas.utils.data_utils import jsonResponse
from django.shortcuts import render_to_response, render_mako
from django.contrib.auth.ldap_helper import LDAPHandler
from django.utils import simplejson
from users.MAUser import MAUser
from madas.users.MAUser import getCurrentUser
from madas.login.URLState import getCurrentURLState
from django.utils import simplejson

def login(request, *args):
    success = processLogin(request, args)
    return HttpResponseRedirect(siteurl(request)) 


def processLogin(request, *args):
    print '***processLogin : enter ***' 

    success = False

    if request.method == "POST":
        post = request.POST.copy()
   
        try:
            username = post['username']
            password = post['password']
        except Exception,e:
            username = ''
            password = ''

        user = None
        from django.contrib.auth import authenticate, login
        try: 
            print 'auth begin'
            user = authenticate(username = username, password = password)
            print 'auth done'
        except Exception, e:
            print str(e)

        authenticated = 0
        authorized = 0
        if user is not None:
            
            print '\tprocessLogin: valid user'
            if user.is_active:
                print '\tprocessLogin: active user'
                print str(user)
                try:
                    a = login(request, user)
                except Exception, e:
                    print str(e)
                print '\tfinished doing auth.login: ', a
                success = True
                authenticated = True
                authorized = True
                #set the session to expire after
                from madas import settings
                request.session.set_expiry(settings.MADAS_SESSION_TIMEOUT)
            else:
                print '\tprocessLogin: inactive user'
                success = False
                authenticated = False 
                authorized = False
        else:
            print '\tprocessLogin: invalid user'
            success = False
            authenticated = False
            authorized = False

        nextview = 'login:success' #the view that a non admin would see next
        
        should_see_admin = False
        request.user.is_superuser = False
        

        madasuser = MAUser()
        madasuser.refresh(request)
        
        for gr in madasuser.CachedGroups:
            if gr == 'Administrators':
                should_see_admin = True
    
        if should_see_admin is True:
            nextview = 'admin:adminrequests'
            request.user.is_superuser = True
            print '\tAdmin! - Setting is_superuser to ', request.user.is_superuser
        else:
            request.user.is_superuser = False
            print '\tNot Admin! - Setting is_superuser to ', request.user.is_superuser

        #if they are authenticated (i.e. they have an entry in django's user table, and used the right password...)
        if authenticated:
            request.user.save() #save the status of is_admin 
        
        u = request.user
        
        params = []
        #redirectMainContentFunction = None 
        #if redirectMainContentFunction is not None and redirectMainContentFunction != '': 
        #    print 'Redirectmaincontentfunction was: ', redirectMainContentFunction
        #    nextview = redirectMainContentFunction
        #    request.session['redirectMainContentFunction'] = None
        #    request.session['params'] = None
               
        mainContentFunction = nextview
        params = params

        print '\tprocessLogin, mainContentFunction: ', mainContentFunction

    print '*** processLogin : exit ***'
    return success 

def processLogout(request, *args):
    from django.contrib.auth import logout
    print '*** processLogout : enter***'
    print '\tlogging out (django)'
    logout(request) #let Django log the user out
    print '*** processLogout : exit***'
    return HttpResponseRedirect(siteurl(request)) 

def processForgotPassword(request, *args):
    '''
    handles the submission of the 'forgot password' form
    regardless of success it should return success, to obfsucate user existence
    sets a validaton key in the user's ldap entry which is used to validate the user when they click the link in email
    '''
    print '*** processForgotPassword : enter***'
    emailaddress = request.REQUEST['username'].strip()
    from madas import settings
    ld = LDAPHandler(userdn=settings.LDAPADMINUSERNAME, password=settings.LDAPADMINPASSWORD)
    u = ld.ldap_get_user_details(emailaddress)
    print 'User details: ', u
    import md5
    m = md5.new()
    import time
    m.update('madas' + str(time.time()) + 'resetPasswordToken123')
    vk = m.hexdigest()

    u['pager'] = [vk]

    #remove groups info
    try:
        del u['groups']
    except:
        pass

    print '\tUpdating user record with verification key'
    ld.ldap_update_user(emailaddress, None, None, u) 
    print '\tDone updating user with verification key'

    #Email the user
    from mail_functions import sendForgotPasswordEmail
    sendForgotPasswordEmail(request, emailaddress, vk)
   
    #$this->getRequest()->setAttribute('params', json_encode(array('message' => 'An email has been sent to '.$email.'. Please follow the instructions in that email to continue')));

    from django.utils import simplejson
    m = simplejson.JSONEncoder()
    p = {}
    p['message'] = "An email has been sent to %s. Please follow the instructions in that email to continue" % (emailaddress)

    print '*** processForgotPassword : exit***'
    return jsonResponse(params=p, mainContentFunction='message') 

def forgotPasswordRedirect(request, *args):
    print '\tEntered forgot password'
    u = request.user
    try:
        print '\tsetting vars'
        #request.session['redirectMainContentFunction'] = 'login:resetpassword'
        #request.session['resetPasswordEmail'] = request.REQUEST['em']
        #request.session['resetPasswordValidationKey'] = request.REQUEST['vk']
        urlstate = getCurrentURLState(request)
        print 'setting mcf'
        urlstate.redirectMainContentFunction = 'login:resetpassword'
        print 'setting em'
        urlstate.resetPasswordEmail = request.REQUEST['em']
        print 'setting vk'
        urlstate.resetPasswordValidationKey = request.REQUEST['vk']
        
        print 'redirecting' 
        return HttpResponseRedirect(siteurl(request))
    except Exception, e:
        print 'there was an exception in forgot password'
        print str(e)

def populateResetPasswordForm(request, *args):
    u = request.user
    print '***populateResetPasswordForm***: enter'
    data = {}
    urlstate = getCurrentURLState(request, andClear=True)
    data['email'] = urlstate.resetPasswordEmail
    data['validationKey'] = urlstate.resetPasswordValidationKey
    print '***populateResetPasswordForm***: exit'
    return jsonResponse(items=[data]) 

def processResetPassword(request, *args):
    print '***populateResetPasswordForm***: enter'
    from madas import settings
    
    username = request.REQUEST.get('email', '')
    vk = request.REQUEST.get('validationKey', '')
    passw = request.REQUEST.get('password', '')
    success = True
    if username is not '' and vk is not '' and passw is not '':

        #get existing details
        ld = LDAPHandler(userdn=settings.LDAPADMINUSERNAME, password=settings.LDAPADMINPASSWORD)
        userdetails = ld.ldap_get_user_details(request.REQUEST['email'])
        if userdetails.has_key('groups'):
            del userdetails['groups'] #remove 'groups' - they don't belong in an update.
        if userdetails.has_key('pager') and len(userdetails['pager']) == 1 and userdetails['pager'][0] == vk:
            #clear out the pager vk
            del userdetails['pager']
            #update the password
            ld.ldap_update_user(username, username, passw, userdetails, pwencoding='md5')
            from mail_functions import sendPasswordChangedEmail
            sendPasswordChangedEmail(request, username)
                
        else:
            print '\tEither no vk stored in ldap, or key mismatch. uservk was %s, storedvk was %s' % (vk, userdetails.get('pager', None))
            success = False

    else:
        print 'Argument error'
        success = False
        request.session.flush() #if we don't flush here, we are leaving the redirect function the same.
    print '***populateResetPasswordForm***: exit'
    return jsonResponse(success=success, mainContentFunction='login') 

#TODO not sure this function is even needed
def unauthenticated(request, *args):
    return jsonResponse() 

#TODO not sure this function is even needed
def unauthorized(request, *args):
    print 'executed Login:unauthorized'
    authorized = False
    mainContentFunction = 'notauthorized'
    #TODO now go to 'pager' with action 'index'
    return jsonResponse(mainContentFunction=mainContentFunction) 

### TODO: not sure this function is even needed
def index(request, *args):
    return jsonResponse() 

def serveIndex(request, *args, **kwargs):
    #print 'serve index...'
    #print 'cruft: ', cruft
    #print 'siteurl: ', siteurl(request)
    #print 'session: '
    #for key in request.session.keys():
    #    print '\t%s: %s' % (key, str(request.session[key]))

    currentuser = getCurrentUser(request)
    mcf = 'dashboard'
    params = ''
    if currentuser.IsLoggedIn:
        #only clear if we were logged in.
        urlstate = getCurrentURLState(request, andClear=True)
    else:
        urlstate = getCurrentURLState(request) 
    
    if urlstate.redirectMainContentFunction:
            mcf = urlstate.redirectMainContentFunction
    if urlstate.params:
        params = urlstate.params
    print 'params: ', params

    if params:
        sendparams = params[1]
    else:
        sendparams = ''

    from django.utils import simplejson
    jsonparams = simplejson.dumps(sendparams)
    #print 'calling render with mcf=', mcf
    #print 'calling render with params=', params

    return render_mako('index.mako', 
                        APP_SECURE_URL = siteurl(request),
                        username = request.user.username,
                        mainContentFunction = mcf,
                        wh = django.utils.webhelpers,
                        params = jsonparams 
                      )

