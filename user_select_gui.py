import os
import time
import datetime
import wx
import MplayerCtrl as mpc
import wx.lib.buttons as buttons

dirName = os.path.dirname(os.path.abspath(__file__))
bitmapDir = os.path.join(dirName, 'bitmaps')

class videoPlayer(wx.Frame):
    def __init__(self, parent, id, title, mplayer):
        wx.Frame.__init__(self, parent, id, title, size = wx.DisplaySize())
        self.panel = wx.Panel(self)
        self.overlay = wx.Overlay()
        sp = wx.StandardPaths.Get()
        self.currentFolder = sp.GetDocumentsDir()
        self.currentVolume = 50
        self.create_menu()
        # create sizers
        mainSizer = wx.BoxSizer(wx.VERTICAL)
        controlSizer = self.build_controls()
        sliderSizer = wx.BoxSizer(wx.HORIZONTAL)

        self.mplayer = mpc.MplayerCtrl(self.panel, -1, mplayer)
        self.playbackSlider = wx.Slider(self.panel, size = wx.DefaultSize)
        sliderSizer.Add(self.playbackSlider, 1, wx.ALL | wx.EXPAND, 5)

        # create volume control
        self.volumeCtrl = wx.Slider(self.panel, style = wx.SL_VERTICAL | wx.SL_INVERSE, size = (-1, 50))
        self.volumeCtrl.SetRange(0, 100)
        self.volumeCtrl.SetValue(self.currentVolume)
        self.volumeCtrl.Bind(wx.EVT_SLIDER, self.on_set_volume)
        controlSizer.Add(self.volumeCtrl, 0, wx.ALL, 5)
        
        # create track counter
        self.trackCounter = wx.StaticText(self.panel, label = "0:00:00")
        sliderSizer.Add(self.trackCounter, 0, wx.ALL | wx.CENTER, 7)
        
        # set up playback timer
        self.playbackTimer = wx.Timer(self)
        self.Bind(wx.EVT_TIMER, self.on_update_playback, self.playbackTimer)

        # bind playback slider to playback timer?
        # self.playbackSlider.Bind(wx.EVT_SLIDER, self.on_set_time)

        mainSizer.Add(self.mplayer, 1, wx.ALL | wx.EXPAND, 5)
        mainSizer.Add(sliderSizer, 0, wx.ALL | wx.EXPAND, 5)
        mainSizer.Add(controlSizer, 0, wx.ALL | wx.CENTER, 5)
        self.panel.SetSizer(mainSizer)
        
        self.panel.Bind(mpc.EVT_MEDIA_STARTED, self.on_media_started)
        self.panel.Bind(mpc.EVT_MEDIA_FINISHED, self.on_media_finished)
        self.panel.Bind(mpc.EVT_PROCESS_STARTED, self.on_process_started)
        self.panel.Bind(mpc.EVT_PROCESS_STOPPED, self.on_process_stopped)
 
        self.Show()
        self.panel.Layout()

    #---------------------------------------------------------
    def build_btn(self, btnDict, sizer):
        bmp = btnDict['bitmap']
        handler = btnDict['handler']
        
        img = wx.Bitmap(os.path.join(bitmapDir, bmp))
        btn = buttons.GenBitmapButton(self.panel, bitmap = img, name = btnDict['name'])
        btn.SetInitialSize()
        btn.Bind(wx.EVT_BUTTON, handler)
        sizer.Add(btn, 0, wx.EXPAND, 3)

    #---------------------------------------------------------
    def build_controls(self):
        """
        Builds the audio bar controls
        """
        controlSizer = wx.BoxSizer(wx.HORIZONTAL)
 
        btnData = [{'bitmap':'player_pause.png', 
                    'handler':self.on_pause, 'name':'pause'},
                   {'bitmap':'player_stop.png',
                    'handler':self.on_stop, 'name':'stop'},
                   {'bitmap':'player_fast_forward.png',
                    'handler':self.on_ff, 'name':'ff'},
                   {'bitmap':'player_crop.png',
                    'handler':self.on_crop, 'name':'crop'}]
        for btn in btnData:
            self.build_btn(btn, controlSizer)
 
        return controlSizer
 
    #----------------------------------------------------------------------
    def create_menu(self):
        """
        Creates a menu
        """
        menubar = wx.MenuBar()
        fileMenu = wx.Menu()
        add_file_menu_item = fileMenu.Append(wx.NewId(), "&Add File", "Add Media File")
        menubar.Append(fileMenu, '&File')
 
        self.SetMenuBar(menubar)
        self.Bind(wx.EVT_MENU, self.on_add_file, add_file_menu_item)
 
    #----------------------------------------------------------------------
    def on_add_file(self, event):
        """
        Add a Movie and start playing it
        """
        wildcard = "Media Files (*.*)|*.*"
        dlg = wx.FileDialog(
            self, message="Choose a file",
            defaultDir=self.currentFolder, 
            defaultFile="",
            wildcard=wildcard,
            style=wx.OPEN | wx.CHANGE_DIR
            )
        if dlg.ShowModal() == wx.ID_OK:
            path = dlg.GetPath()
            self.currentFolder = os.path.dirname(path[0])
            trackPath = '"%s"' % path.replace("\\", "/")
            self.mplayer.Loadfile(trackPath)
            self.playbackTimer.Start()
            self.mplayer.Start(mplayer_args=[u'--no-fs'])
 
    #----------------------------------------------------------------------
    def on_media_started(self, event):
        print 'Media started!'
        t_len = self.mplayer.GetTimeLength()
        print "total length of video: " + str(t_len)
        print "video resolution: " + str(self.mplayer.GetVideoResolution())
        self.playbackSlider.SetRange(0, int(t_len + 1))
        self.playbackTimer.Start(100)
 
    #----------------------------------------------------------------------
    def on_media_finished(self, event):
        print 'Media finished!'
        self.playbackTimer.Stop()
 
    #----------------------------------------------------------------------
    def on_pause(self, event):

        if self.playbackTimer.IsRunning():
            print "pausing..."
            print self.mplayer.GetTimePos()
            self.mplayer.Pause()
            self.playbackTimer.Stop()
            
        else:
            print "unpausing..."
            self.mplayer.Pause()
            self.playbackTimer.Start()
 
    #----------------------------------------------------------------------
    def on_crop(self, event):
        # pause video if it hasn't been paused yet
        if self.playbackTimer.IsRunning():
            self.on_pause(event)
        # bind to mouse clicks to draw rectangle
        self.mplayer.Bind(wx.EVT_LEFT_DOWN, self.start_rectangle)
        self.mplayer.Bind(wx.EVT_LEFT_UP, self.finish_rectangle)

    #----------------------------------------------------------------------
    def start_rectangle(self, event):
        self.start_pos = event.GetPosition()
        self.mplayer.Bind(wx.EVT_MOTION, self.intermediate_rectangle)
        print "start rectangle at " + str(self.start_pos)

    #----------------------------------------------------------------------
    def redraw_rectangle(self, pos):
        rect = wx.RectPP(self.start_pos, pos)
        dc = wx.ClientDC(self.mplayer)
        odc = wx.DCOverlay(self.overlay, dc)
        odc.Clear()
        dc.SetPen(wx.Pen(wx.RED, 1, wx.SOLID))
        dc.SetBrush(wx.Brush("grey", style = wx.TRANSPARENT))
        dc.DrawRectangleRect(rect)
        del odc #bug in python, this makes sure odc destroyed before dc
    
    #----------------------------------------------------------------------
    def enforce_ratio(self, pos):
        # make sure selected rectangle is 4:3 ratio.  If it's not, find closest
        # point on same plane that would make it correct
        width = abs(self.start_pos.x - pos.x)
        required_height = int(float(3) / 4 * width)
        if pos.y < self.start_pos.y:
            return (pos.x, self.start_pos.y - required_height)
        else:
            return (pos.x, self.start_pos.y + required_height)

    #----------------------------------------------------------------------
    def intermediate_rectangle(self, event):
        # redraw intermediate rectangles, so user knows what it looks like so far
        if event.Dragging and event.LeftIsDown():
            intermediate_pos = self.enforce_ratio(event.GetPosition())
            self.redraw_rectangle(intermediate_pos)

    #----------------------------------------------------------------------
    def finish_rectangle(self, event):
        self.finish_pos = self.enforce_ratio(event.GetPosition())
        self.redraw_rectangle(self.finish_pos)
        dc = wx.ClientDC(self)
        odc = wx.DCOverlay(self.overlay, dc)
        odc.Clear()
        del odc
        self.overlay.Reset()
        print "finish rectangle"        

    #----------------------------------------------------------------------
    def on_ff(self, event):
        print "speeding up by 1.25 x"
        self.mplayer.SpeedMult(1.25)

    #----------------------------------------------------------------------
    def on_process_started(self, event):
        print 'Process started!'
 
    #----------------------------------------------------------------------
    def on_process_stopped(self, event):
        print 'Process stopped!'
 
    #----------------------------------------------------------------------
    def on_set_volume(self, event):
        """
        Sets the volume of the music player
        """
        self.currentVolume = self.volumeCtrl.GetValue()
        self.mplayer.SetProperty("volume", self.currentVolume)
  
    #----------------------------------------------------------------------
    def on_set_time(self, event):
        """
        Sets the video according to playback slider
        """
        current_seconds = self.GetValue()
        self.mplayer.Seek(self.current_seconds, 2)
    #----------------------------------------------------------------------
    def on_stop(self, event):

        print "stopping..."
        self.mplayer.Stop()
        self.playbackTimer.Stop()
 
    #----------------------------------------------------------------------
    def on_update_playback(self, event):
        """
        Updates playback slider and track counter
        """
        try:
            offset = self.mplayer.GetTimePos()
        except:
            return
        # print "on_update_playback offset: " + str(offset)
        secs_played = int(offset)
        self.playbackSlider.SetValue(secs_played)
        self.trackCounter.SetLabel(str(datetime.timedelta(seconds=secs_played)))
    
class app(wx.App):
    def OnInit(self):
        frame = videoPlayer(None, -1, 'Hello', u'mplayer')
        self.SetTopWindow(frame)
        frame.Show()
        return 1

if __name__ == "__main__":
    prog = app(0)
    prog.MainLoop()
