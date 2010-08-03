# Create your views here.
from django.http import HttpResponse
from django.utils import simplejson
from mdatasync_server.models import *
from repository.models import *  
from mdatasync_server.rules import *
from django.conf import settings
import os
import os.path

def jsonResponse(data):
    jdata = simplejson.dumps(data)
    return HttpResponse(jdata)

#nodeconfig = NodeConfig()
########nodeconfig.AddRule('testnode', 'teststation', '*.swp', ActionType.UPDATE_EXISTING)
#####nodeconfig.AddRule('testnode', 'teststation', '/testsource,/testdest', ActionType.MOVE)
#nodeconfig.AddRule('testnode', 'teststation', '*.pdf', ActionType.EXCLUDE)
#nodeconfig.AddRule('testnode', 'teststation', 'always/**', ActionType.INCLUDE)

def configureNode(request, *args):
    return jsonResponse(nodeconfig.toDict())

def getNodeClients(request, *args):
    print 'trying getNodeClients'
    ncs = NodeClient.objects.all()
    result = {}
    for n in ncs:
        print 'checking a node'
        if not result.has_key(n.organisation_name):
            result[n.organisation_name] = {}
        o = result[n.organisation_name]
        if not o.has_key(n.site_name):
            o[n.site_name] = []

        o[n.site_name].append(n.station_name)

    return jsonResponse(result)

def retrievePathsForFiles(request, *args):
    status = 0 #no error
    error = '' #no error
    filesdict = {} 
    rules = []
    import webhelpers
    #default host is this host.
    host = None 
    defaultHost = request.__dict__['META']['SERVER_NAME'] 
    flags = None
    username = None

    try:
        pfiles = request.POST.get('files', {})
        #pfiles is json for a list of filenames
        pfiles = simplejson.loads(pfiles)
        #pfiles is now our list of fnames.
        porganisation = simplejson.loads(request.POST.get('organisation', ''))
        psitename= simplejson.loads(request.POST.get('sitename', ''))
        pstation = simplejson.loads(request.POST.get('stationname', ''))
        print 'Post var files passed through was: ', pfiles
        print 'Post var organisation passed through was: ', porganisation
        print 'Post var station passed through was: ', pstation
        print 'Post var sitename passed through was: ', psitename

        #filter by client, node, whatever to 
        #get a list of filenames in the repository run samples table
        #to compare against.
        #for each filename that matches, you use the experiment's ensurepath 
        try:
            nodeclient = NodeClient.objects.get(organisation_name = porganisation, site_name=psitename, station_name = pstation)
            print 'Nodeclient found.'
            nchost = nodeclient.hostname
            if nchost is not None and len(nchost) > 0:
                host = str(nchost)
            ncflags = nodeclient.flags
            if ncflags is not None and len(ncflags) > 0:
                flags = str(ncflags)
            ncuname = nodeclient.username
            if ncuname is not None and len(ncuname) > 0:
                username = str(ncuname)

            try:
                rulesset = NodeRules.objects.filter(parent_node = nodeclient)
                rules = [x.__unicode__() for x in rulesset]
            except Exception, e:
                status = 1
                error = '%s, %s' % (error, 'Unable to resolve ruleset: %s' % (str(e)))
            #now get the runs for that nodeclient
            runs = Run.objects.filter(machine = nodeclient) 
            for run in runs:
                runsamples = RunSample.objects.filter(run = run)
                for rs in runsamples:
                    fname = rs.filename;
                    abspath, relpath = rs.filepaths()
                    print 'Filename: %s belongs in path %s' % ( fname, abspath )
                    if filesdict.has_key(fname):
                        print 'Duplicate path detected!!!'
                        error = "%s, %s" % (error, "Duplicate filename detected for %s" % (fname))
                        status = 2
                    #we use the relative path    
                    filesdict[fname] = [run.id, rs.id, relpath]

        except Exception, e:
            status = 1
            error = "%s, %s" % (error, 'Unable to resolve end machine to stored NodeClient: %s' % str(e) )
        

    except Exception, e:
        status = 1
        error = str(e)

    retfilesdict = {}
    runsamplesdict = {}

    #so by this stage, we can go through and test each sent file against the filesdict.
    for fname in pfiles:
        fname = str(fname)
        if fname in filesdict.keys(): #filesdict is keyed on filename
            retfilesdict[fname] = filesdict[fname][2] #relative path is third item in the list
            runid = filesdict[fname][0]
            runsampleid = filesdict[fname][1]
            if runid not in runsamplesdict.keys():
                runsamplesdict[runid] = []
            runsamplesdict[runid].append(runsampleid) 
            print 'Setting %s to %s' % (fname, retfilesdict[fname])
        else:
            print '%s not associated with a runsample. Ignored' % (fname)

    #set the default host
    if host is None or len(host) == 0:
        host = defaultHost 

    retval = {'status': status,
             'error' : error,
             'filesdict':retfilesdict,
             'runsamplesdict' : runsamplesdict,
             'rootdir' : settings.REPO_FILES_ROOT,
             'rules' : rules,
             'host' : host,
             'username': username,
             'flags': flags,
             #'rules' : None 
            }

    print 'RETVAL is', retval
    return jsonResponse(retval)

def checkRunSampleFiles(request):
    ret = {}
    ret['success'] = False;
    ret['description'] = "No Error"
    runsamplefilesjson = request.POST.get('runsamplefiles', None)
    if runsamplefilesjson is not None:
        runsamplefilesdict = simplejson.loads(runsamplefilesjson)
        #so now we have a dict keyed on run, of sample id's whose file should have been received.
        print 'Checking run samples against:', runsamplefilesdict
        #We iterate through each run, get the samples referred to, and ensure their file exists on disk.
        ret['description'] = ""
        for runid in runsamplefilesdict.keys():
            print 'Checking files from run %s', str(runid)
            runsamples = runsamplefilesdict[runid]
            for runsample in runsamples:
                runsample = int(runsample)
                try:
                    rs = RunSample.objects.get(id = runsample)
                    abssamplepath, relsamplepath = rs.filepaths()
                    complete_filename = os.path.join(abssamplepath, rs.filename)
                    fileexists = os.path.exists(complete_filename)
                    print 'Checking file %s:%s' % (complete_filename, str(fileexists))
                    
                    #now change the value in the DB
                    rs.complete = fileexists
                    rs.save()
                    ret['success'] = True 
                    ret['description'] = 'Success'
                except Exception, e:
                    ret['success'] = False
                    ret['description'] = "%s, %s" % (ret['description'], str(e)) 
                
    else:
        ret['description'] = "No files given"

    return jsonResponse(ret)

def defaultpage(request, *args):
    try:
        pfiles = request.POST.get('files', None)
        porganisation = simplejson.loads(request.POST.get('organisation', ''))
        psitename= simplejson.loads(request.POST.get('sitename', ''))
        pstation = simplejson.loads(request.POST.get('stationname', ''))
        print 'Post var files passed through was: ', pfiles
        print 'Post var organisation passed through was: ', porganisation
        print 'Post var station passed through was: ', pstation
        print 'Post var sitename passed through was: ', psitename

        #try to get a config for this node/station
        try:
            ncs = NodeClient.objects.filter(organisation_name = porganisation, site_name = psitename, station_name = pstation)
            rulesset = NodeRules.objects.filter(parent_node = ncs)
        except:
            print 'Could not get a matching nodeclient'
        n = ncs[0]
        print 'Current nodeconfig is : ', n 
        rules = [x.__unicode__() for x in rulesset]
        path = '%s/pending/%s/%s/%s' % (settings.PERSISTENT_FILESTORE, porganisation, psitename, pstation)
        
        #make sure the path exists
        if not os.path.exists(path):
            print 'Creating %s' % (path)
            try:
                os.makedirs(path)
            except:
                print 'Could not make the path!'

        import webhelpers
        host = request.__dict__['META']['SERVER_NAME'] #might not be right name
        #host = request.__dict__['META']['REMOTE_ADDR'] #might be client address?
        #host = request.__dict__['META']['HTTP_HOST'] #would include port

        #hardcoded return
        d = {'host':host,
             'path':path,
             'rules' : rules
             #'rules' : None 
            }
        print 'rules DICT: ', d
        return jsonResponse(d)
    except Exception, e:
        return jsonResponse(str(e))


def logUpload(request, *args):
    fname_prefix = 'UNKNOWN_'
    if request.POST.has_key('nodename'):
        fname_prefix = request.POST['nodename'] + '_'
    
    if request.FILES.has_key('uploaded'):
        f = request.FILES['uploaded']
        print 'Uploaded file name:', f._get_name()
        _handle_uploaded_file(f, str(os.path.join('synclogs', "%s%s" % (fname_prefix,'rsync.log')) ) )#dont allow them to replace arbitrary files
    else:
        print 'No file in the post'

    return jsonResponse('ok')

def keyUpload(request, *args):
    fname_prefix = 'UNKNOWN_'
    if request.POST.has_key('nodename'):
        fname_prefix = request.POST['nodename'] + '_'
    
    if request.FILES.has_key('uploaded'):
        f = request.FILES['uploaded']
        print 'Uploaded file name:', f._get_name()
        _handle_uploaded_file(f, str(os.path.join('publickeys', "%s%s" % (fname_prefix,'id_rsa.pub')) ) )#dont allow them to replace arbitrary files
    else:
        print 'No file in the post'

    return jsonResponse('ok')



def _handle_uploaded_file(f, name):
    '''Handles a file upload to the projects REPO_FILES_ROOT
       Expects a django InMemoryUpload object, and a filename'''
    print '*** _handle_uploaded_file: enter ***'
    retval = False
    try:
        import os
        dest_fname = str(os.path.join(settings.REPO_FILES_ROOT, name))
        if not os.path.exists(os.path.dirname(dest_fname)):
            print 'creating directory: ', os.path.dirname(dest_fname)
            os.makedirs(os.path.dirname(dest_fname))

        destination = open(dest_fname, 'wb+')
        for chunk in f.chunks():
            destination.write(chunk)
        destination.close()
        retval = True
    except Exception, e:
        retval = False
        print '\tException in file upload: ', str(e)
    print '*** _handle_uploaded_file: exit ***'
    return retval


'''
def defaultpage(request, *args):
    try:

        pfiles = request.POST.get('files', None)
        porganisation = simplejson.loads(request.POST.get('organisation', ''))
        psitename= simplejson.loads(request.POST.get('sitename', ''))
        pstation = simplejson.loads(request.POST.get('station', ''))
        print 'Post var files passed through was: ', pfiles
        print 'Post var organisation passed through was: ', porganisation
        print 'Post var station passed through was: ', pstation
        print 'Post var sitename passed through was: ', psitename

        #try to get a config for this node/station
        n = nodeconfig.toDict()
        print 'Current nodeconfig is : ', n 
        if n.has_key(porganisation) and n[porganisation].has_key(psitename):
            rules = n[pnode][pstation] 
        else:
            rules = None
        #hardcoded return
        d = {'host':'127.0.0.1',
             'path':'/tmp/madas/filedata/pending/%s' % (pstation),
             'rules' : rules
             #'rules' : None 
            }
        print 'rules DICT: ', d
        return jsonResponse(d)
    except Exception, e:
        return jsonResponse(str(e))
'''



