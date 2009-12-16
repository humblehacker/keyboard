import wx
from copy import deepcopy
from textwrap import fill

from util import Rect, Point, Size
from notifications import KeyUpdateNotification, ModelChangeNotification

class DisplayKey(object):

    def __init__(self, handle, unscaled):
        "A DisplayKey handle may be, but is not neccessarily, the same as " \
        "a SourceKey handle"
        self._handle = handle
        self.unscaled = unscaled
        self.scaled = None

    def getHandle(self):
        return self._handle

    def __str__(self):
        return "{%s: unscaled: %s scaled: %s}" % (self._handle, self.unscaled, self.scaled)

    handle = property(lambda self : self.getHandle())

DRAG_MODE_NONE     = 0
DRAG_MODE_START    = 1
DRAG_MODE_DRAGGING = 2

DISPLAY_MODE_DYNAMIC_RESIZE = 0
DISPLAY_MODE_WRAPPED        = 1

class KeyDisplayPane(wx.ScrolledWindow):

    def __init__(self, parent, displayMode, border):
        wx.ScrolledWindow.__init__(self, parent)
        self._displayKeys = {}
        self._orderedHeyHandles = []
        self._keySize = wx.Size(4, 4)
        self._keySpacing = wx.Size(1, 1)
        self._border = border
        self._selectedKeyHandle = None
        self._contentSize = Size(200, 200)
        self._displayMode = displayMode
        self._scroll = wx.Size(0, 0)
        self._scrollUnit = wx.Size(0, 0)
        self._tooltip = wx.ToolTip("")
        self._zoom = 1
        if displayMode == DISPLAY_MODE_DYNAMIC_RESIZE:
            self._zoom = 10 # 25
        self._dragStart = None
        self._dragMode = DRAG_MODE_NONE
        self.Bind(wx.EVT_PAINT, self.OnPaint)
        self.Bind(wx.EVT_SIZE, self.OnSize)
        self.Bind(wx.EVT_MOUSE_EVENTS, self.OnMouse)
        self.Bind(wx.EVT_CHAR, self.OnChar)
        self.Bind(wx.EVT_KILL_FOCUS, self.OnKillFocus)
        self.Bind(wx.EVT_SET_FOCUS, self.OnSetFocus)
        self.SetToolTip(self._tooltip)
        self.SetScrollRate(1, 1)

        displayRect = self._getDisplayRect()
        print "displayRect: %s" % displayRect
#           dc.SetMapMode(wx.MM_TEXT)
        dc.SetMapMode(wx.MM_METRIC)
        contentRect = Rect(dc.DeviceToLogicalX(displayRect.x), dc.DeviceToLogicalY(displayRect.y),
                           dc.DeviceToLogicalXRel(displayRect.width), dc.DeviceToLogicalYRel(displayRect.height))


    def _initKeys(self):
        self._selectedKeyHandle = None

    def _updateScrollbars(self):
        self._updateKeys()
        self.SetScrollRate(self._scrollUnit.width, self._scrollUnit.height)
        self.SetVirtualSize(self._scroll)

    def _getScale(self, rect):
        # if scaled, scale is a ratio of content size to rect size
        # otherwise, scale is based on the width of the letter 'W'
        # in the current system font.
        if self._displayMode == DISPLAY_MODE_DYNAMIC_RESIZE:
            scale = float(rect.width) / self._contentSize.width
            if self._contentSize.height * scale <= rect.height:
                return scale / self._zoom
            return (float(rect.height) / self._contentSize.height) / self._zoom
        else:
            dc = wx.WindowDC(self)
            (w, h) = dc.GetTextExtent('W')
            return w

    def _getDisplayRect(self):
        clientRect = self.GetClientRect()
        displayRect = wx.Rect(*clientRect)
        displayRect.Deflate(self._border, self._border)
        return displayRect

    def _refreshKey(self, displayKey):
        scale = 1
        if self._displayMode == DISPLAY_MODE_DYNAMIC_RESIZE:
            scale = self._getScale(self._getDisplayRect())
        rect = displayKey.scaled
        rect = rect * scale
        self.RefreshRect(rect.Inflate(2 * self._zoom, 2 * self._zoom).Get())

    def _selectKey(self, displayKeyHandle):
        if not self._isKeySelected(displayKeyHandle):

            # de-select existing selection
            if self._selectedKeyHandle:
                displayKey = self._displayKeys[self._selectedKeyHandle]
                self._selectedKeyHandle = None
                self._refreshKey(displayKey);

            # select new key
            if displayKeyHandle:
                self._selectedKeyHandle = displayKeyHandle
                displayKey = self._displayKeys[self._selectedKeyHandle]
                self._refreshKey(displayKey);
                KeyUpdateNotification(displayKeyHandle).notify()

    def _isKeySelected(self, displayKeyHandle):
        return self._selectedKeyHandle != None and self._selectedKeyHandle == displayKeyHandle

    def GetSelectedKeyHandle(self):
        return self._selectedKeyHandle

    def _updateKeys(self):
        """
        Adjust position and scale of each display key based on current display rect.
        """
        displayRect = self._getDisplayRect()
        self._scroll.width = self._scroll.height = 0
        self._scrollUnit = displayRect.size
        scale = self._getScale(displayRect)

        if self._displayMode == DISPLAY_MODE_DYNAMIC_RESIZE:
            print scale
            contentRect = deepcopy(displayRect)
            if scale > 0:
                adjustedSize = Size(self._contentSize.width  * scale * self._zoom,
                                    self._contentSize.height * scale * self._zoom )
                contentRect.width  = adjustedSize.width
                contentRect.height = adjustedSize.height
                contentRect = contentRect.CenterIn(displayRect)
                contentRect.x /= scale
                contentRect.y /= scale

            for displayKey in self._displayKeys.values():
                displayKey.scaled = displayKey.unscaled * self._zoom
                displayKey.scaled.OffsetXY(contentRect.x, contentRect.y)
        else:
            maxWidth = displayRect.width / scale
            origin = Point(0, 0)
            for displayKeyHandle in self._orderedHeyHandles:
                displayKey = self._displayKeys[displayKeyHandle]
                if origin.x + self._keySize.width > maxWidth:
                    origin.x = 0
                    origin.y += self._keySize.height + self._keySpacing.height
                displayKey.unscaled.x = origin.x
                displayKey.unscaled.y = origin.y
                displayKey.scaled = displayKey.unscaled * scale
                self._scroll.width = max(self._scroll.width, displayKey.scaled.x + displayKey.scaled.width)
                self._scroll.height = max(self._scroll.height, displayKey.scaled.y + displayKey.scaled.height)
                displayKey.scaled.OffsetXY(displayRect.x, displayRect.y)
                origin.x += self._keySize.width + self._keySpacing.width
                self._scrollUnit.width = min(self._scrollUnit.width, displayKey.scaled.width)
                self._scrollUnit.height = min(self._scrollUnit.height, displayKey.scaled.height)
            self._scroll.width  += self._border * 2
            self._scroll.height += self._border * 2
            self._scrollUnit.width  += self._keySpacing.width  * scale
            self._scrollUnit.height += self._keySpacing.height * scale

    def OnSize(self, event):
        self._updateScrollbars()
        self.Refresh()

    def OnMouse(self, event):
        if event.Moving():
            displayKeyHandle = self._hitTest(event.GetPosition())
            if displayKeyHandle != None:
                self._tooltip.SetTip("\n%s" % displayKeyHandle)
                self._tooltip.Enable(True)
            else:
                self._tooltip.Enable(False)

        elif event.LeftUp():
            displayKeyHandle = self._hitTest(event.GetPosition())
            self._selectKey(displayKeyHandle)
            self._dragMode = DRAG_MODE_NONE

        elif event.LeftDown():
            self._dragStart = event.GetPosition()
            self._dragMode = DRAG_MODE_START

        elif event.Dragging() and self._dragMode != DRAG_MODE_NONE:

            if self._dragMode == DRAG_MODE_START:
                # are we dragging yet?
                tolerance = 2
                dx = abs(event.GetPosition().x - self._dragStart.x)
                dy = abs(event.GetPosition().y - self._dragStart.y)
                if dx <= tolerance and dy <= tolerance:
                    return

                # start the drag
                self._dragMode = DRAG_MODE_DRAGGING
                displayKeyHandle = self._hitTest(self._dragStart)
                data = wx.TextDataObject(displayKeyHandle)
                dropSource = wx.DropSource(self)
                dropSource.SetData(data)
                result = dropSource.DoDragDrop(wx.Drag_AllowMove)
                if result == wx.DragMove:
                    pass

        event.Skip()

    def OnChar(self, event):
        if self._selectedKeyHandle == None:
            self._selectKey(self._displayKeys.keys()[0])
        displayKey = self._displayKeys[self._selectedKeyHandle]
        pos = None
        code = event.GetKeyCode()
        if code == wx.WXK_LEFT:
            pos = Point(displayKey.unscaled.x - self._keySpacing.width - 1,
                        displayKey.unscaled.y)
        elif code == wx.WXK_RIGHT:
            pos = Point(displayKey.unscaled.x + displayKey.unscaled.width + self._keySpacing.width + 1,
                        displayKey.unscaled.y)
        elif code == wx.WXK_UP:
            pos = Point(displayKey.unscaled.x,
                        displayKey.unscaled.y - self._keySpacing.height - 1)
        elif code == wx.WXK_DOWN:
            pos = Point(displayKey.unscaled.x,
                        displayKey.unscaled.y + displayKey.unscaled.height + self._keySpacing.height + 1)
        else:
            event.Skip()
            return

        selectKeyHandle = None
        for (displayKeyHandle, displayKey) in self._displayKeys:
            if displayKey.unscaled.Contains(pos):
                selectKeyHandle = displayKeyHandle
                break
        if selectKeyHandle != None:
            self._selectKey(selectKeyHandle)

    def _hitTest(self, point):
        """
        Given a point in device coordinates, return a handle to the display
        key that contains the point, or None if no corresponding display key is
        found
        """
        point = self.CalcUnscrolledPosition(point)
        if self._displayMode == DISPLAY_MODE_DYNAMIC_RESIZE:
            dc = wx.WindowDC(self)
            displayRect = self._getDisplayRect()
            scale = self._getScale(displayRect)
            dc.SetMapMode(wx.MM_TEXT)
            dc.SetUserScale(scale, scale)
            (point.x, point.y) = (dc.DeviceToLogicalX(point.x), dc.DeviceToLogicalY(point.y))

        for displayKey in self._displayKeys.values():
            if displayKey.scaled.Contains(point):
                return displayKey.handle
        return None

    def _drawKeys(self, dc):
        blackPen = wx.Pen('black')
        whiteBrush = wx.Brush('white')
        font = wx.Font(10, wx.FONTFAMILY_SWISS, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL, False, 'Arial Rounded MT Bold')
        dc.SetFont(font)
        scale = 1

        if self._displayMode == DISPLAY_MODE_DYNAMIC_RESIZE:
            displayRect = self._getDisplayRect()
            print "displayRect: %s" % displayRect
#           dc.SetMapMode(wx.MM_TEXT)
            dc.SetMapMode(wx.MM_METRIC)
            contentRect = Rect(dc.DeviceToLogicalX(displayRect.x), dc.DeviceToLogicalY(displayRect.y),
                               dc.DeviceToLogicalXRel(displayRect.width), dc.DeviceToLogicalYRel(displayRect.height))
            print "contentRect: %s" % contentRect
            scale = self._getScale(contentRect)
#           dc.SetPen(wx.Pen('black', 1*scale))
            dc.SetMapMode(wx.MM_TEXT)

        for displayKey in self._displayKeys.values():
#           if self._isKeySelected(displayKey.handle):
#               if self.FindFocus() == self:
#                   # TODO: Generalize this magic number from system
#                   #       settings.  Currently is Mac selection blue.
#                   dc.SetPen(wx.Pen('#3e75d6', 2))
#               else:
#                   dc.SetPen(wx.Pen('dark grey', 2))
#               dc.SetBrush(wx.Brush('light grey'))
#           else:
#               dc.SetPen(blackPen)
#               dc.SetBrush(whiteBrush)
            label_rect = deepcopy(displayKey.scaled)
            key_rect   = deepcopy(displayKey.scaled)

            # make any necessary adjustments
            if self._displayMode == DISPLAY_MODE_DYNAMIC_RESIZE:
                key_rect = key_rect * scale

            # draw key rectangle
            dc.DrawRoundedRectangleRect(key_rect.Get(), -.075)

            # draw label
            if False:
                label_rect.Deflate(5, 2)
                label = self._getLabel(displayKey)
                if label:
                    dc.SetUserScale(scale, scale)
                    (width, height) = dc.GetTextExtent(label)
                    if width > label_rect.width:
                        # TODO: better wrapping
    #                   extents = dc.GetPartialTextExtents(label)
                        label = fill(label, 5)
                    dc.DrawLabel(label, label_rect.Get(), wx.ALIGN_LEFT|wx.ALIGN_BOTTOM)
                    if self._isKeySelected(displayKey.handle):
                        dc.SetPen(blackPen)
                        dc.SetBrush(whiteBrush)
                    dc.SetUserScale(1, 1)

    def _getLabel(self, displayKey):
        return displayKey.handle

    def OnPaint(self, event):
        dc = wx.PaintDC(self)
        self.DoPrepareDC(dc)
        self._drawKeys(dc)


    def OnKillFocus(self, event):
        self.Refresh()

    def OnSetFocus(self, event):
        if self._selectedKeyHandle:
            KeyUpdateNotification(self._selectedKeyHandle).notify()
        self.Refresh()

if __name__ == '__main__':
    app = wx.PySimpleApp()
    frame = wx.Frame(None, -1, 'keydisplay')
    pane = KeyDisplayPane(frame, displayMode=DISPLAY_MODE_WRAPPED, border=10)
    pane._getDisplayRect()

