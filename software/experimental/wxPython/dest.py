import wx
import cPickle

from util import Rect, Point, say
from notifications import KeyUpdateNotification, ModelChangeNotification, \
                          LayerChangeNotification
from keydisplay import KeyDisplayPane, DisplayKey, DISPLAY_MODE_DYNAMIC_RESIZE
from keyboard import KeyRef
from model import Model

class DestDisplayKey(DisplayKey):

    def __init__(self, location, sourcekeyHandle, unscaled):
        DisplayKey.__init__(self, sourcekeyHandle, unscaled)
        self._location = location

    def _getDisplayHandle(self):
        return self._location

    def _getLocation(self):
        return self._location

    location = property(_getLocation)

class DestDropTarget(wx.DropTarget):

    def __init__(self, parent):
        wx.DropTarget.__init__(self)
        self.parent = parent
        self.data = wx.CustomDataObject('sourcekey handle')
        self.SetDataObject(self.data)

#   def OnDrop(self, x, y):
#       dlg = wx.MessageDialog(self.parent, "Dropped at (%d, %d)" % (x, y),
#                              "Dropping", wx.OK | wx.ICON_INFORMATION)
#       dlg.ShowModal()
#       dlg.Destroy()

    def OnData(self, x, y, default):
        data = None
        self.GetData()
        sourceHandle = cPickle.loads(self.data.GetData())
        self.parent.DoDrop(x, y, sourceHandle)
        return default

class DestPane(wx.Notebook):

    def __init__(self, parent):
        wx.Notebook.__init__(self, parent)
        parent.SetBackgroundColour(wx.SystemSettings.GetColour(wx.SYS_COLOUR_BTNFACE))

        LayerChangeNotification.AddObserver(self.NotifyLayerChange)

        for keymap in Model.keyboard.maps:
            page = DestPage(self, keymap)
            self.AddPage(page, keymap.ids[-1], wx.ID_ANY)

        self.SetSelection(0)

    def NotifyLayerChange(self, notification):
        layer = notification.layer
        index = 0
        for keymap in Model.keyboard.maps:
            if keymap.ids[-1] == layer:
                break
            index += 1
        self.SetSelection(index)
        self.Refresh()

class DestPage(KeyDisplayPane):

    def __init__(self, parent, keymap):
        self._kb = Model.keyboard
        KeyDisplayPane.__init__(self, parent, border=10, displayMode=DISPLAY_MODE_DYNAMIC_RESIZE)
        self._keymap = keymap
        ModelChangeNotification.AddObserver(self.NotifyModelChange)
        self.SetBackgroundColour(wx.SystemSettings.GetColour(wx.SYS_COLOUR_BTNFACE))
        dt = DestDropTarget(self)
        self.SetDropTarget(dt)

    def _initKeys(self):
        self._keySpacing = wx.Size(self._kb.layout.spacing, self._kb.layout.spacing)
        self._displayKeys = {}
        selectedKey = None
        rows = self._kb.layout.rows
        for row in rows:
            if row is None:
                continue
            for keydef in row.keydefs:
                if keydef.isNullKey:
                    continue
                keyRect = Rect(keydef.origin.x, keydef.origin.y, keydef.size.width, keydef.size.height)
                location = keydef.location
                keyHandle = None
                if self._keymap and self._keymap.keys.has_key(location):
                    keyHandle = self._keymap.keys[location].keyHandle
                self._displayKeys[location] = DestDisplayKey(location, keyHandle, keyRect)
                if selectedKey == None:
                    selectedKey = location

        self._updateKeys()
        self._selectKey(selectedKey)

    def GetSelectedKeyHandle(self):
        if self._selectedKeyHandle:
            return self._displayKeys[self._selectedKeyHandle].sourceHandle

    def NotifyModelChange(self, notification):
        self._initKeys()

    def DoDrop(self, x, y, sourceHandle):
        displayKey = self._hitTest(wx.Point(x, y))
        if not displayKey:
            print "You missed"
            return
        self._keymap.keys[displayKey.location] = KeyRef(displayKey.location, sourceHandle)
        ModelChangeNotification(None).notify()

    def _getLabels(self, displayKey):
        if self._keymap and self._keymap.keys.has_key(displayKey.location):
            keyref = self._keymap.keys[displayKey.location]
            sourceKey = Model.sourcekeys[keyref.keyHandle]
            return sourceKey.labels
        return None

    def _getContentSize(self):
        return self._kb.maxSize

def main():
    from model import Model

    Model.StaticInit()
    app = wx.PySimpleApp()
    frame = wx.Frame(None, -1, 'dest')
    pane = DestPane(frame)
    frame.Show()
    app.MainLoop()


if __name__ == '__main__':

    main()

