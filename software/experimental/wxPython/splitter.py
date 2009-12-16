import sys

import wx
import wx.gizmos

class MacSplitterWindow(wx.SplitterWindow):
    """Subclass of the standard wx.SplitterWindow to provide a more modern
    Mac-like splitter sash"""

    def __init__(self, parent, style):
        # style is ignored
        wx.SplitterWindow.__init__(self, parent, style=wx.SP_LIVE_UPDATE|wx.SP_3DSASH)
        self.SetBackgroundColour('#A5A5A5')
        self.Bind(wx.EVT_PAINT, self.OnPaint)
        self.Bind(wx.EVT_SPLITTER_SASH_POS_CHANGED, self.OnSashPosChanged)
        self.Bind(wx.EVT_SPLITTER_SASH_POS_CHANGING, self.OnSashPosChanging)

    def OnPaint(self, event):
        dc = wx.PaintDC(self)
        self.DrawSash(dc)
        event.Skip()

    def OnSashPosChanged(self, event):
        event.Skip()

    def OnSashPosChanging(self, event):
        event.Skip()
        pass

    def DrawSash(self, dc):
        pos = self.GetSashPosition()
        height = self.GetSashSize()

        if self.GetSplitMode() == wx.SPLIT_HORIZONTAL:
            sz = dc.GetSize()
            dc.GradientFillLinear((0, pos+1, sz.width, height-2), '#FCFCFC', '#DFDFDF', wx.SOUTH)

    def SplitHorizontally(self, window1, window2, sashPos):
#       self.SetSashSize(10)
        wx.SplitterWindow.SplitHorizontally(self, window1, window2, sashPos)

    def SplitVertically(self, window1, window2, sashPos):
        self.SetSashSize(1)
        wx.SplitterWindow.SplitVertically(self, window1, window2, sashPos)

    def InitBuffer(self):
        w, h = self.GetClientSize()
        self.buffer = wx.EmptyBitmap(w, h)
        dc = wx.BufferedDC(wx.ClientDC(self), self.buffer)
        self.DrawSash(dc)

if sys.platform == 'darwin':
    SplitterWindow = MacSplitterWindow
else:
    SplitterWindow = wx.SplitterWindow

if __name__ == '__main__':
    app = wx.PySimpleApp()

    hframe = wx.Frame(None, -1, 'source', pos=(200,200), size=(400,400))
    hsp = SplitterWindow(hframe, style=(wx.SP_LIVE_UPDATE|wx.SP_3D))
    left = wx.Panel(hsp)
    right = wx.Panel(hsp)
    left.SetBackgroundColour("white")
    right.SetBackgroundColour("white")
    left.Hide()
    hsp.Initialize(right)
    hsp.SetMinimumPaneSize(10)
    hsp.SplitHorizontally(left, right, 100)
    hframe.Show()

    vframe = wx.Frame(hframe, -1, 'source', pos=(650,200), size=(400,400))
    vsp = SplitterWindow(vframe, style=(wx.SP_LIVE_UPDATE|wx.SP_3D))
    left = wx.Panel(vsp)
    right = wx.Panel(vsp)
    left.SetBackgroundColour("white")
    right.SetBackgroundColour("grey")
    left.Hide()
    vsp.Initialize(right)
    vsp.SetMinimumPaneSize(10)
    vsp.SplitVertically(left, right, 100)
    vframe.Show()

    app.MainLoop()



