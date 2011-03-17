from django.http import HttpResponse, HttpResponseForbidden, HttpResponseUnauthorized
from madas.users.MAUser import MAUser

#We check the user is logged in,
#and then grab the user details off the session,
#including cached groups
def admins_only(f):
    def new_function(*args, **kwargs):
        request = args[0]
        if not request.user.is_authenticated():
            return HttpResponseUnauthorized()
        mauser = request.session.get('mauser', None)

        if mauser is None:
            mauser = MAUser()
            mauser.refresh()
            mauser = request.session.get('mauser', None)

        if mauser.IsAdmin:
            return f(*args, **kwargs)
        else:
            return HttpResponseForbidden()
    return new_function
