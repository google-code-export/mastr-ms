from madas.utils.data_utils import jsonResponse, jsonErrorResponse
from madas.users.MAUser import loadMadasUser

def submit(request, *args):
    '''This adds a new user into ldap with no groups
    '''
    print '*** registration/submit ***' 

    import madas.users 
    from madas.users.views import _usersave
    
    if {} == loadMadasUser(request.REQUEST['email']):
        oldstatus, status =  _usersave(request, request.REQUEST['email'], admin=False)
        
        #HACK, save again to try to put the password in
        oldstatus, status =  _usersave(request, request.REQUEST['email'], admin=False)

        from mail_functions import sendRegistrationToAdminEmail
        
        sendRegistrationToAdminEmail(request, 'trac-nema@ccg.murdoch.edu.au')
        
        return jsonResponse(request)
    else:
        return jsonErrorResponse('User already exists')
    print '*** registration/submit end ***' 
