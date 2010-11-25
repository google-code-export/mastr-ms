import wx
import urllib2
from poster.encode import multipart_encode
from poster import streaminghttp
try: import json as simplejson
except ImportError: import simplejson

import NodeConfigSelector

from identifiers import *
import  wx.lib.filebrowsebutton as filebrowse

#register the streamind http and https handlers with urllib2
streaminghttp.register_openers()

class Preferences(wx.Dialog):
    def __init__(self, parent, ID, config, log):
        # Instead of calling wx.Dialog.__init__ we precreate the dialog
        # so we can set an extra style that must be set before
        # creation, and then we create the GUI object using the Create
        # method.

        self.preference_keys = ['localdir', 'user', 'updateurl']

        pre = wx.PreDialog()
        pre.SetExtraStyle(wx.DIALOG_EX_CONTEXTHELP)
        pre.Create(parent, ID, 'Preferences', wx.DefaultPosition, wx.DefaultSize, wx.DEFAULT_FRAME_STYLE)
        pre.width = 400
        #Turn the object into a proper dialog wrapper.
        self.PostCreate(pre)

        
        self.log = log
        self.parentApp = parent
        self.config = config

        # Now continue with the normal construction of the dialog
        # contents
        sizer = wx.BoxSizer(wx.VERTICAL)
        #label = wx.StaticText(self, -1, "DataSync Preferences")
        #label.SetHelpText("Preference settings for the DataSync application")
        #sizer.Add(label, 0, wx.ALIGN_CENTER|wx.ALL, 2)

        self.nodeconfigselector = None 
        #Get the rest of the config
        k = self.config.getConfig().keys()
        k.sort()

        #report current node config name, and give button to choose
        box = wx.BoxSizer(wx.HORIZONTAL)
        self.nodeconfiglabel = wx.StaticText(self, -1, "" ) 
        self.setNodeConfigLabel()
        #box.Add(label, 1, wx.ALIGN_LEFT|wx.ALL, 2)
        
        sizer.Add(box, 1, wx.GROW|wx.ALIGN_CENTER_VERTICAL|wx.ALL, 2)
        self.nodeconfigselector = NodeConfigSelector.NodeConfigSelector(self, ID_NODESELECTOR_DIALOG, self.log, None)
    
        #self.nodeconfigselector.createTree()
        sizer.Add(self.nodeconfigselector, 6, wx.GROW|wx.ALL, 2)


        buttonsbox = wx.BoxSizer(wx.HORIZONTAL)
        #and a button to upload keys 
        keybutton = wx.Button(self, ID_SENDKEY_BUTTON)
        keybutton.SetLabel("Send Key")
        keybutton.Bind(wx.EVT_BUTTON, self.OnSendKey)
        buttonsbox.Add(keybutton, 1, wx.ALIGN_LEFT | wx.ALL, 2)

        self.keybutton = keybutton

        #and a 'handshake' button
        hsbutton = wx.Button(self, ID_HANDSHAKE_BUTTON)
        hsbutton.SetLabel("Handshake")
        hsbutton.Bind(wx.EVT_BUTTON, self.OnHandshake)
        buttonsbox.Add(hsbutton, 1, wx.ALIGN_LEFT | wx.ALL, 2)

        self.keybutton = keybutton
        self.handshakebutton = hsbutton

        sizer.Add(buttonsbox, 1, wx.GROW|wx.ALIGN_CENTER_VERTICAL|wx.ALL, 2)

        self.fields = {}
        for key in self.preference_keys:
            if self.config.getShowVar(key):
                box = wx.BoxSizer(wx.HORIZONTAL)
                if key == 'localdir':
                    ctrl = filebrowse.DirBrowseButton(self, -1, size=(450, -1), changeCallback = None, labelText=self.config.getFormalName(key), startDirectory = str(self.config.getValue(key)) )
                    ctrl.SetValue(str(self.config.getValue(key)) )
                    box.Add(ctrl, 1, wx.ALIGN_RIGHT|wx.ALL, border=0)
                else: 
                    label = wx.StaticText(self, -1, self.config.getFormalName(key))
                    label.SetHelpText(self.config.getHelpText(key))
                    box.Add(label, 0, wx.ALIGN_LEFT| wx.ALIGN_CENTER_VERTICAL|wx.ALL, border=0)
                    #the text entry field
                    ctrl = wx.TextCtrl(self, -1, str(self.config.getValue(key)) ) #, size=(80,-1))
                    ctrl.SetHelpText(self.config.getHelpText(key))
                    box.Add(ctrl, 1, wx.ALIGN_RIGHT|wx.ALL, border=2)
                sizer.Add(box, 1, wx.GROW|wx.ALIGN_CENTER_VERTICAL|wx.ALL, border=0)
                
                #store the field so we can serialise it later
                self.fields[key] = ctrl

        btnsizer = wx.StdDialogButtonSizer()
        
        if wx.Platform != "__WXMSW__":
            btn = wx.ContextHelpButton(self)
            btnsizer.AddButton(btn)
        
        btn = wx.Button(self, wx.ID_OK)
        btn.SetHelpText("The OK button completes the dialog")
        btn.SetDefault()
        btnsizer.AddButton(btn)
        btn.Bind(wx.EVT_BUTTON, self.OKPressed)
        
        btn = wx.Button(self, wx.ID_CANCEL)
        btn.SetHelpText("Cancel changes")
        btnsizer.AddButton(btn)
        btnsizer.Realize()
        
        sizer.Add(btnsizer, 1, wx.ALIGN_CENTER_VERTICAL|wx.ALL, border=0)

        self.SetSizer(sizer)
        sizer.Fit(self)

    
    def OKPressed(self, *args):
        self.save(args)
        self.EndModal(0)

    def OnSendKey(self, evt):
        print 'send keys!'
        self.keybutton.Disable()
        origlabel = self.keybutton.GetLabel()
        self.keybutton.SetLabel('Sending')

        try:
            #Start the multipart encoded post of whatever file our log is saved to:
            posturl = self.config.getValue('synchub') + 'keyupload/'

            keyfile = open('id_rsa.pub')
            datagen, headers = multipart_encode( {'uploaded' : keyfile, 'nodename' : self.config.getNodeName()} )
            request = urllib2.Request(posturl, datagen, headers)
            print 'sending log %s to %s' % (keyfile, posturl)
            jsonret = urllib2.urlopen(request).read()
            retval = simplejson.loads(jsonret)
            print 'OnSendKey: retval is %s' % (retval)
            self.log('Key send response: %s' % (str(retval)) )
        except Exception, e:
            print 'OnSendKey: Exception occured: %s' % (str(e))
            self.log('Exception occured sending key: %s' % (str(e)), type=self.log.LOG_ERROR)


        self.keybutton.Enable()
        self.keybutton.SetLabel(origlabel)

    def OnHandshake(self, evt):
        print 'OnHandshake!'
        self.parentApp.MSDSHandshakeFn(returnFn=None)

    def save(self, *args):
        #k = self.config.getConfig().keys()
        for key in self.preference_keys:
            if self.config.getShowVar(key): #if this is var shown on this dialog (not in the tree)
                print 'Setting config at %s to %s' % (str(key), self.fields[key].GetValue())
                self.config.setValue(key, self.fields[key].GetValue())

        #call the method that will serialise the config.
        self.config.save()
        self.parentApp.resetTimeTillNextSync()


    def setNodeConfigLabel(self):
        self.nodeconfiglabel.SetLabel("Current Node: %s" % (self.config.getNodeName()) ) 

    #this function gets called by the node chooser dialog,
    #and uses the data it passes to put values into the config, which arent 
    #collected in the 'save' method above.
    def setNodeConfigName(self, datadict):
        for k in datadict.keys():
            self.config.setValue(k, datadict[k])
        self.setNodeConfigLabel()
        
    #def openNodeChooser(self, *args):
    #    self.nodeconfigselector = NodeConfigSelector.NodeConfigSelector(self, ID_NODESELECTOR_DIALOG, self.log, None)
    #
    #    self.nodeconfigselector.createTree()
    #    self.nodeconfigselector.ShowModal()
    #    self.nodeconfigselector.Destroy()

    def postRsyncLog(self, *args):
        import MultipartPostHandler, urllib2, sys
        opener = urllib2.build_opener(MultipartPostHandler.MultipartPostHandler)
        params = {'uploaded' : open("rsync.log")}
        a = opener.open(self.config.getValue('synchub') + 'logupload/')
        resp = a.read()
        print resp

    def postRSAKey(self, *args):
        pass