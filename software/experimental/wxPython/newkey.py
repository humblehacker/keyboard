import wx
import re

from util import Rect, Point, say, Size
from notifications import KeyUpdateNotification, ModelChangeNotification, \
                          LayerChangeNotification
from keydisplay import KeyDisplayPane, DisplayKey, DISPLAY_MODE_DYNAMIC_RESIZE, \
                       DISPLAY_MODE_WRAPPED
from model import Model, SourceKey, MacroKey
from hid import Usage


class NewKeyDropTarget(wx.DropTarget):

    def __init__(self, parent):
        wx.DropTarget.__init__(self)
        self.parent = parent
        self.data = wx.TextDataObject()
        self.SetDataObject(self.data)

#   def OnDrop(self, x, y):
#       dlg = wx.MessageDialog(self.parent, "Dropped at (%d, %d)" % (x, y),
#                              "Dropping", wx.OK | wx.ICON_INFORMATION)
#       dlg.ShowModal()
#       dlg.Destroy()

    def OnData(self, x, y, default):
        self.GetData()
        actualData = self.data.GetText()
        self.parent.DoDrop(x, y, actualData)
        return default


class TestPane(wx.Panel):

    def __init__(self, parent):
        wx.Panel.__init__(self, parent, size=(200, 200))
        self.Bind(wx.EVT_PAINT, self.OnPaint)

    def OnPaint(self, event):
        dc = wx.PaintDC(self)
        rect = self.GetClientRect()
        dc.SetPen(wx.Pen('black'))
        dc.DrawRectangleRect(rect)
        dc.DrawLabel("%s (%s, %s)" % (self.__class__.__name__, rect.width, rect.height), rect.Get(),
                     wx.ALIGN_CENTER)


class NewKeyPane(wx.Panel):

    def __init__(self, parent, keyHandle=None):
        wx.Panel.__init__(self, parent)

        self.okButton = wx.Button(self, wx.ID_OK)
        self.cancelButton = wx.Button(self, wx.ID_CANCEL)

        sourceKey = None
        if keyHandle is not None:
            sourceKey = Model.sourcekeys[keyHandle]
        else:
            sourceKey = SourceKey(None)
        assert(sourceKey is not None)

        dispPane  = DispPane(self, sourceKey)
        macroPane = MacroPane(self, sourceKey)
        modPane   = ModifierKeyPane(self)

        leftSizer = wx.BoxSizer(wx.VERTICAL)
        leftSizer.Add(dispPane, proportion=1, flag=wx.EXPAND)
        leftSizer.Add(modPane,  proportion=1, flag=wx.EXPAND)

        upperSizer = wx.BoxSizer(wx.HORIZONTAL)
        upperSizer.Add(leftSizer, proportion=1, flag=wx.EXPAND)
        upperSizer.Add(macroPane,  proportion=2, flag=wx.EXPAND)

        btnSizer = wx.StdDialogButtonSizer()
        btnSizer.AffirmativeButton = self.okButton
        btnSizer.CancelButton = self.cancelButton
        btnSizer.Realize()

        mainSizer = wx.BoxSizer(wx.VERTICAL)
        mainSizer.Add(upperSizer, proportion=1, flag=wx.EXPAND)
        mainSizer.Add(btnSizer, flag=wx.EXPAND|wx.ALL, border=10)
        self.SetSizer(mainSizer)

        mainSizer.Fit(self)
        mainSizer.SetSizeHints(self)


class DispPane(KeyDisplayPane):

    def __init__(self, parent, sourceKey):
        KeyDisplayPane.__init__(self, parent, border=10, displayMode=DISPLAY_MODE_DYNAMIC_RESIZE)
        self._sourceKey = sourceKey
        self._dispKey = DisplayKey(sourceKey.handle, Rect(0, 0, 1.8, 1.8))
        self._displayKeys = {sourceKey.handle:self._dispKey}
        self._updateKeys()
        KeyDisplayPane._initKeys(self)

    def _getContentSize(self):
        return Size(1.8, 1.8)

#   def OnPaint(self, event):
#       dc = wx.PaintDC(self)
#       rect = self.GetClientRect()
#       dc.DrawRectangleRect(rect)
#       KeyDisplayPane.OnPaint(self, event)

class MacroPane(KeyDisplayPane):

    def __init__(self, parent, sourceKey):
        KeyDisplayPane.__init__(self, parent, border=10, displayMode=DISPLAY_MODE_WRAPPED)
        self._displayKeys = {}
        KeyDisplayPane._initKeys(self)
        self.Bind(wx.EVT_PAINT, self.OnPaint)
        self._keySize = Size(6.0, 2.5)
        self._keySpacing = Size(0.2, 0.2)
        keyRect = Rect(0, 0, *self._keySize)
        handle = None
        if sourceKey.usage:
            handle = sourceKey.usage.MakeHandle()
        elif sourceKey.mode:
            handle = "mode:%s" % sourceKey.mode
        elif len(sourceKey.macro) > 0:
            for (i, macroKey) in enumerate(sourceKey.macro):
                handle = macroKey.MakeHandle(i)
                self._displayKeys[handle] = DisplayKey(handle, keyRect)
                self._orderedKeyHandles.append(handle)
            handle = None
        if handle is not None:
            dispKey = DisplayKey(handle, keyRect)
            self._displayKeys[handle] = dispKey
            self._orderedKeyHandles.append(handle)
            self._updateKeys()

    def _getLabels(self, displayKey):
        labels = {}
        print displayKey.handle
        keyInfo = re.split(':', displayKey.handle)
        if keyInfo[0] == 'usage':
            labels['TopLeft'] = "page: %s id: %s" % (keyInfo[1], keyInfo[2])
        elif keyInfo[0] == 'mode':
            labels['TopLeft'] ="mode: %s" % keyInfo[1]
        elif keyInfo[0] == 'macro':
            labels['BottomLeft'] = "modifiers: %s " % keyInfo[4]
            labels['TopLeft'] = "page: %s id: %s" % (keyInfo[2], keyInfo[3])
        elif keyInfo[0] == 'm_usage':
            labels['TopLeft'] = "page: %s id: %s" % (keyInfo[2], keyInfo[3])
        else:
            labels['BottomLeft'] = "?"
        return labels

    def OnPaint(self, event):
        dc = wx.PaintDC(self)
        rect = self.GetClientRect()
        dc.DrawRectangleRect(rect)
        KeyDisplayPane.OnPaint(self, event)


class ModifierKeyPane(KeyDisplayPane):

    def __init__(self, parent):
        KeyDisplayPane.__init__(self, parent, border=0, displayMode=DISPLAY_MODE_DYNAMIC_RESIZE)
        self._initKeys()

    def _initKeys(self):
        KeyDisplayPane._initKeys(self)
        self._displayKeys = { 'left_shift':  DisplayKey('left_shift',  Rect(0.0, 0.0, 2.8, 1.8)),
                              'left_ctrl':   DisplayKey('left_ctrl',   Rect(0.0, 2.0, 2.8, 1.8)),
                              'left_alt':    DisplayKey('left_alt',    Rect(0.0, 4.0, 2.8, 1.8)),
                              'left_gui':    DisplayKey('left_gui',    Rect(0.0, 6.0, 2.8, 1.8)),
                              'right_shift': DisplayKey('right_shift', Rect(3.0, 0.0, 2.8, 1.8)),
                              'right_ctrl':  DisplayKey('right_ctrl',  Rect(3.0, 2.0, 2.8, 1.8)),
                              'right_alt':   DisplayKey('right_alt',   Rect(3.0, 4.0, 2.8, 1.8)),
                              'right_gui':   DisplayKey('right_gui',   Rect(3.0, 6.0, 2.8, 1.8)) }
        self._updateKeys()

    def _getContentSize(self):
        return Size(6.0, 8.0)

def main():
    app = wx.PySimpleApp()
    frame = wx.Frame(None, -1, 'dest')
    pane = NewKeyPane(frame)
    frame.Show()
    app.MainLoop()

if __name__ == '__main__':

    main()

