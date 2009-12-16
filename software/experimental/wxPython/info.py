import wx
from wx.lib.foldpanelbar import *

from notifications import KeyUpdateNotification, LayerChangeNotification, ModelChangeNotification
from model import Model

class InfoFrame(wx.MiniFrame):

    def __init__(self, parent, pos=wx.DefaultPosition, size=wx.DefaultSize):
        wx.MiniFrame.__init__(self, parent, -1, pos = pos, size = size,
                              style=(wx.CAPTION|wx.RESIZE_BORDER|
                                     wx.CLOSE_BOX|wx.MINIMIZE_BOX|wx.MAXIMIZE_BOX))
        self._info = InfoPanel(self)
        self.Bind(wx.EVT_MAXIMIZE, self.OnMaximize)

    def OnMaximize(self, event):
        rect = self.GetParent().GetRect()
        self.SetPosition((rect.x+rect.width, rect.y))
        self.SetSize((200, rect.height))

    def Maximize(self):
        pass

class InfoPanel(FoldPanelBar):

    def __init__(self, parent):
        FoldPanelBar.__init__(self, parent, wx.ID_ANY, wx.DefaultPosition,
                             wx.DefaultSize, FPB_DEFAULT_STYLE,
                             FPB_COLLAPSE_TO_BOTTOM)

        KeyUpdateNotification.AddObserver(self.NotifyKeyUpdate)
        LayerChangeNotification.AddObserver(self.NotifyLayerChange)
        ModelChangeNotification.AddObserver(self.NotifyModelChange)
        ModelChangeNotification(None).notify()

#       model.addListener(self.OnUpdateModel)

        item = self.AddFoldPanel("Keyboard", False)
        self.AddFoldPanelWindow(item, wx.StaticText(item, -1, "Vendor: %s" % Model.keyboard.org))
        self.AddFoldPanelWindow(item, wx.StaticText(item, -1, "Layout: %s" % Model.keyboard.layout.eid))

        item = self.AddFoldPanel("Keymap", False)
        choicePanel = wx.Panel(item, -1)
        text = wx.StaticText(choicePanel, -1, "Layer: ")
        self.layersChoice = wx.Choice(choicePanel, -1, choices=self.layers)
        sizer = wx.BoxSizer(wx.HORIZONTAL)
        sizer.AddF(text, wx.SizerFlags().Proportion(0))
        sizer.AddF(self.layersChoice, wx.SizerFlags().Proportion(1).Expand())
        choicePanel.SetSizer(sizer)
        choicePanel.Fit()
        self.AddFoldPanelWindow(item, choicePanel)
        self.Bind(wx.EVT_CHOICE, self.OnChangeLayer)

        item = self.AddFoldPanel("Key", False)
        self.keyIdTxt = wx.StaticText(item, -1, "Key id: ");
        self.AddFoldPanelWindow(item, self.keyIdTxt)
        self.AddFoldPanelWindow(item, wx.StaticText(item, -1, "Usage Page: "))
        self.AddFoldPanelWindow(item, wx.StaticText(item, -1, "Usage ID: "))

        self.NotifyKeyUpdate(None)

#       self.AddFoldPanelSeparator(item)

        # now add a text ctrl. Also very easy. Align this on width so that
        # when the control gets wider the text control also sizes along.
#       self.AddFoldPanelWindow(item, wx.TextCtrl(item, wx.ID_ANY, "Comment"),
#                                FPB_ALIGN_WIDTH, FPB_DEFAULT_SPACING, 20)

    def NotifyModelChange(self, notification):
        self.layers = [map.ids[-1] for map in Model.keyboard.maps]

    def NotifyKeyUpdate(self, notification):
        if notification != None:
            keyId = notification.eid
        else:
            keyId = "No selection"
        self.keyIdTxt.SetLabel("Key id: %s" % keyId)

    def OnChangeLayer(self, event):
        choice = event.GetEventObject()
        layer = choice.GetStringSelection()
        LayerChangeNotification(layer).notify()

    def NotifyLayerChange(self, notification):
        idx = self.layersChoice.FindString(notification.layer)
        if self.layersChoice.GetSelection() != idx:
            self.layersChoice.SetSelection(idx)

if __name__ == '__main__':
    app = wx.PySimpleApp()
    frame = wx.Frame(None, -1, "Info")
    from model import Model
    Model.StaticInit()
    info = InfoFrame(frame)
    frame.Show()
    info.Show()
    app.MainLoop()


