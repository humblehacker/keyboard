import sys

import wx
import wx.lib.colourdb

import data
from util import Point, Rect
from splitter import SplitterWindow
from keydisplay import KeyDisplayPane, DisplayKey, DISPLAY_MODE_WRAPPED
from notifications import KeyUpdateNotification, CategoryChangeNotification
from model import Model


class SourcePane(SplitterWindow):

    def __init__(self, parent):
        SplitterWindow.__init__(self, parent, style=(wx.SP_LIVE_UPDATE|wx.SP_3D))
        self.SetSashGravity(0.5)
        left = CategoryPane(self)
        right = SelectorPane(self)
        left.Hide()
        self.Initialize(right)
        self.SetMinimumPaneSize(10)
        self.SplitVertically(left, right, 200)


class CategoryPane(wx.Panel):

    def __init__(self, parent):
        wx.Panel.__init__(self, parent)
        self.content = wx.TreeCtrl(self, style=(wx.TR_DEFAULT_STYLE|wx.NO_BORDER|wx.TR_HIDE_ROOT))
        self.Bind(wx.EVT_TREE_SEL_CHANGED, self.OnSelChanged, self.content)
        root = self.content.AddRoot('Root')

        for category in Model.categories:
            self.content.AppendItem(root, category)
        self.content.SetBackgroundColour('#E7EDF6')

        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.AddF(self.content, wx.SizerFlags().Proportion(1).Expand())
        self.SetSizer(sizer)
        self.Fit()

    def OnSelChanged(self, event):
        category = self.content.GetItemText(event.GetItem())
        CategoryChangeNotification(category).notify()


class SelectorPane(KeyDisplayPane):

    def __init__(self, parent):
        KeyDisplayPane.__init__(self, parent, border=10, displayMode=DISPLAY_MODE_WRAPPED)
        self._category = None
        CategoryChangeNotification.AddObserver(self.NotifyCategoryChange)
        color = wx.SystemSettings.GetColour(wx.SYS_COLOUR_WINDOW)
        self.SetBackgroundColour(color)

    def NotifyCategoryChange(self, notification):
        self._category = Model.categories[notification.category]
        self._initKeys()
        self.Refresh()

    def _initKeys(self):
        KeyDisplayPane._initKeys(self)
        self._displayKeys.clear()
        self._orderedKeyHandles = self._category.keyHandles
        for keyHandle in self._category.keyHandles:
            if not Model.sourcekeys.has_key(keyHandle):
                raise RuntimeError("Unknown key '%s' in category '%s'" % (keyHandle, self._category.name))
            sourceKey = Model.sourcekeys[keyHandle]
            rect = Rect(0, 0, self._keySize.width, self._keySize.height)
            self._displayKeys[keyHandle] = DisplayKey(keyHandle, rect)
        self._updateKeys()
        self._selectKey(self._orderedKeyHandles[0])
        self._updateScrollbars()

    def _getLabel(self, displayKey):
        if Model.sourcekeys.has_key(displayKey.handle):
            sourceKey = Model.sourcekeys[displayKey.handle]
            if sourceKey.labels.has_key('BottomLeft'):
                return sourceKey.labels['BottomLeft']
            if sourceKey.labels.has_key('TopLeft'):
                return sourceKey.labels['TopLeft']
        return ''


if __name__ == '__main__':
    from model import Model
    app = wx.PySimpleApp()
    Model.StaticInit()
    frame = wx.Frame(None, -1, 'source', pos=(200,200), size=(500,400))
    pane = SourcePane(frame)
    frame.Show()
    app.MainLoop()

