# -*- coding: latin-1 -*-
import sys

import wx
from wx.lib.foldpanelbar import *

from model import Model
from dest import DestPane
from source import SourcePane
from newkey import NewKeyPane
from util import Size
from splitter import SplitterWindow
from info import InfoFrame, InfoPanel
from notifications import LayerChangeNotification, ModelChangeNotification

class MainFrame(wx.Frame):

    def __init__(self):
        self._initpos = 100
        wx.Frame.__init__(self, None, -1, 'Remapper', pos=(100,100), size=(800,600))
        self._infoFrame = None
        self._statusbar = self.CreateStatusBar()
        self._sourcePane = None
        self._destPane = None
        self._newKeyPane = None
        self._createToolbar()
        self._createMenubar()
        self._createSplitter()
        self.Bind(wx.EVT_LEFT_DCLICK, self.OnDoubleClick)
        LayerChangeNotification.AddObserver(self.NotifyLayerChange)
        LayerChangeNotification(Model.keyboard.maps[0].ids[-1]).notify()
        ModelChangeNotification(None).notify()

    def OnDoubleClick(self, event):
        dlg = wx.MessageDialog(self, "Double Click!", "Hey!", wx.OK | wx.ICON_INFORMATION)
        dlg.ShowModal()
        dlg.Destroy()

    def _createToolbar(self):
        toolbar = self.CreateToolBar();
        bmp = wx.Image("hand_point3.gif", wx.BITMAP_TYPE_GIF).ConvertToBitmap()
        tool = toolbar.AddSimpleTool(-1, bmp, "The Finger")
        toolbar.Realize()

    def _createSplitter(self):
        self._sp = SplitterWindow(self, style=(wx.SP_LIVE_UPDATE))
        self._sourcePane = SourcePane(self._sp)
        self._destPane = DestPane(self._sp)
        self._sourcePane.Hide()
        self._sp.Initialize(self._destPane)
        self._sp.SplitHorizontally(self._sourcePane, self._destPane, self._initpos)
        if sys.platform == 'darwin':
            # WORKAROUND: the position parameter passed to SplitVertically
            # (see SourcePane.__init__()) seems to be ignored.
            self._sourcePane.SetSashPosition(200)

    def _createMenubar(self):
        # File menu
        fileMenu = wx.Menu()
        item = fileMenu.Append(-1, text = "&New Key...")
        self.Bind(wx.EVT_MENU, self.OnNewKey, item)
        item = fileMenu.Append(-1, text = "&Edit Key...")
        self.Bind(wx.EVT_MENU, self.OnEditKey, item)
        item = fileMenu.Append(wx.ID_ANY, text = "&Open...")
        item = fileMenu.Append(wx.ID_EXIT, text = "&Exit")
        item = fileMenu.Append(wx.ID_PREFERENCES, text = "&Preferences")

        self.Bind(wx.EVT_MENU, self.OnQuit, item)
        self.Bind(wx.EVT_MENU, self.OnOpen, item)
        self.Bind(wx.EVT_MENU, self.OnPrefs, item)

        # Help Menu
        helpMenu = wx.Menu()
        item = helpMenu.Append(wx.ID_HELP, "&Help")
        self.Bind(wx.EVT_MENU, self.OnHelp, item)
        ## this gets put in the App menu on OS-X
        item = helpMenu.Append(wx.ID_ABOUT, "&About", "More information About this program")
        self.Bind(wx.EVT_MENU, self.OnAbout, item)

        # View menu
        viewMenu = wx.Menu()
        item = viewMenu.Append(-1, "Show Info\tCtrl+I")
        self.Bind(wx.EVT_MENU, self.OnShowInfo, item)
        item = viewMenu.Append(-1, "Show Source pane")

        # Actions menu
        actionsMenu = wx.Menu()
        item = actionsMenu.Append(-1, "Upload", "Upload changes to keyboard")
        item = actionsMenu.Append(-1, "Download", "Download existing key maps from keyboard")
        item = actionsMenu.Append(-1, "Reset", "Reset the keyboard to factory settings")

        # Layers menu
        layersMenu = wx.Menu()
        for map in Model.keyboard.maps:
            item = layersMenu.AppendRadioItem(-1, map.ids[-1])
            self.Bind(wx.EVT_MENU, self.OnChangeLayer, item)
        layersMenu.AppendSeparator()
        item = layersMenu.Append(-1, "New Layer")
        self.Bind(wx.EVT_MENU, self.OnNewLayer, item)

        # create the menu bar
        menuBar = wx.MenuBar()
        menuBar.Append(fileMenu,    "&File")
        menuBar.Append(actionsMenu, "Actions")
        menuBar.Append(layersMenu,  "Layers")
        menuBar.Append(viewMenu,    "View")
        menuBar.Append(helpMenu,    "&Help")
        self.SetMenuBar(menuBar)

    def _createInfopanel(self):
        rect = self.GetRect()
        self._infoFrame = InfoFrame(self,
                                     pos=(rect.x+rect.width+1, rect.y),
                                     size=(200, rect.height))

    def OnQuit(self,Event):
        self.Destroy()

    def OnAbout(self, event):
        dlg = wx.MessageDialog(self, "Keyboard remapper for the TypeMatrix 2030\n"
                                     "© 2007 David Whetstone",
                                "About Remapper", wx.OK | wx.ICON_INFORMATION)
        dlg.ShowModal()
        dlg.Destroy()

    def OnHelp(self, event):
        dlg = wx.MessageDialog(self, "The gods help them that help themselves.\n"
                                     "--  Aesop",
                               "Remapper Help", wx.OK | wx.ICON_INFORMATION)
        dlg.ShowModal()
        dlg.Destroy()

    def OnOpen(self, event):
        dlg = wx.MessageDialog(self, "This would be an open Dialog\n"
                                     "If there was anything to open\n",
                                "Open File", wx.OK | wx.ICON_INFORMATION)
        dlg.ShowModal()
        dlg.Destroy()

    def OnPrefs(self, event):
        dlg = wx.MessageDialog(self, "This would be an preferences Dialog\n"
                                     "If there were any preferences to set.\n",
                                "Preferences", wx.OK | wx.ICON_INFORMATION)
        dlg.ShowModal()
        dlg.Destroy()

    def OnNewLayer(self, event):
        dlg = wx.MessageDialog(self, "Yay!  A new layer!",
                               "New Layer", wx.OK | wx.ICON_INFORMATION)
        dlg.ShowModal()
        dlg.Destroy()

    def OnChangeLayer(self, event):
        item = self.GetMenuBar().FindItemById(event.GetId())
        layer = item.GetText()
        LayerChangeNotification(layer).notify()

    def NotifyLayerChange(self, notification):
        menuBar = self.GetMenuBar()
        layers = menuBar.GetMenu(menuBar.FindMenu("Layers"))
        item = layers.FindItemById(layers.FindItem(notification.layer))
        if not item.IsChecked():
            item.Check()

    def OnNewKey(self, event):
        if self._newKeyPane == None:
            self._newKeyPane = NewKeyPane(self._sp)
            self.Bind(wx.EVT_BUTTON, self.OnNewKeyCancel, self._newKeyPane.cancelButton)
            self.Bind(wx.EVT_BUTTON, self.OnNewKeyOK, self._newKeyPane.okButton)
            self._sp.ReplaceWindow(self._destPane, self._newKeyPane)
            self._destPane.Hide()
        else:
            wx.Bell()

    def OnNewKeyOK(self, event):
        self._sp.ReplaceWindow(self._newKeyPane, self._destPane)
        self._destPane.Show()
        self._newKeyPane.Destroy()
        self._newKeyPane = None

    def OnNewKeyCancel(self, event):
        print "hello"
        self._sp.ReplaceWindow(self._newKeyPane, self._destPane)
        self._destPane.Show()
        self._newKeyPane.Destroy()
        self._newKeyPane = None

    def OnEditKey(self, event):
        if self._newKeyPane == None:
            keyHandle = self._getSelectedKeyHandle()
            self._newKeyPane = NewKeyPane(self._sp, keyHandle)
            self.Bind(wx.EVT_BUTTON, self.OnNewKeyOK, self._newKeyPane.okButton)
            self._sp.ReplaceWindow(self._destPane, self._newKeyPane)
            self._destPane.Hide()
        else:
            wx.Bell()

    def _getSelectedKeyHandle(self):
        window = self.FindFocus()
        return window.GetSelectedKeyHandle()

    def OnShowInfo(self, event):
        if self._infoFrame == None:
            self._createInfopanel()
        item = self.GetMenuBar().FindItemById(event.GetId())
        if self._infoFrame.IsShown():
            self._infoFrame.Hide()
            item.SetText('Show Info\tCtrl+I')
        else:
            self._infoFrame.Show()
            item.SetText('Hide Info\tCtrl+I')

    def OnClick(self, event):
        kb = repr(Model.keyboard.org)
        self.button.SetLabel(kb)

if __name__ == '__main__':
    app = wx.PySimpleApp()
    Model.StaticInit()
    frame = MainFrame()
    frame.Show()
    app.MainLoop()
