import wx
from copy import deepcopy
from textwrap import fill
import cPickle

from model import Model
from util import Rect, Point, Size
from notifications import KeyUpdateNotification, ModelChangeNotification

class DisplayKey(object):

    def __init__(self, handle, unscaled):
        """
        A DisplayKey handle may be, but is not necessarily, a SourceKey handle
        """
        self._handle = handle
        self.unscaled = unscaled
        self.scaled = None

    def _getDisplayHandle(self):
        return self._handle

    def _getSourceHandle(self):
        return self._handle

    def __str__(self):
        return "{%s: unscaled: %s scaled: %s}" % (self._handle, self.unscaled, self.scaled)

    handle = property(lambda self : self._getDisplayHandle())
    sourceHandle = property(lambda self : self._getSourceHandle())


DRAG_MODE_NONE     = 0
DRAG_MODE_START    = 1
DRAG_MODE_DRAGGING = 2

DISPLAY_MODE_DYNAMIC_RESIZE = 0
DISPLAY_MODE_WRAPPED        = 1

class KeyDisplayPane(wx.ScrolledWindow):

    def __init__(self, parent, displayMode, border):
        wx.ScrolledWindow.__init__(self, parent)
        self._displayKeys = {}
        self._orderedKeyHandles = []
        self._keySize = Size(1.8, 1.8)
        self._keySpacing = Size(0.2, 0.2)
        self._border = border
        self._selectedKeyHandle = None
        self._displayMode = displayMode
        self._scroll = wx.Size(0, 0)
        self._scrollUnit = wx.Size(0, 0)
        self._tooltip = wx.ToolTip("")
        self._dragStart = None
        self._dragMode = DRAG_MODE_NONE
        self._fontSize = 10
        self.Bind(wx.EVT_PAINT, self.OnPaint)
        self.Bind(wx.EVT_SIZE, self.OnSize)
        self.Bind(wx.EVT_MOUSE_EVENTS, self.OnMouse)
        self.Bind(wx.EVT_CHAR, self.OnChar)
        self.Bind(wx.EVT_KILL_FOCUS, self.OnKillFocus)
        self.Bind(wx.EVT_SET_FOCUS, self.OnSetFocus)
        self.SetToolTip(self._tooltip)
        self.SetScrollRate(1, 1)
        self._createContextMenu()

    def _createContextMenu(self):
        self._contextMenu = wx.Menu()
        item = self._contextMenu.Append(-1, text = "New Key...")
        self.Bind(wx.EVT_MENU, self.OnNewKey, item)
        self._contextMenu.AppendSeparator()
        item = self._contextMenu.Append(-1, text = "Edit Key...")
        self.Bind(wx.EVT_MENU, self.OnEditKey, item)
        self.Bind(wx.EVT_CONTEXT_MENU, self.OnContextMenu)

    def OnContextMenu(self, event):
        pos = event.GetPosition()
        pos = self.ScreenToClient(pos)
        displayKey = self._hitTest(pos)
        self._selectKey(displayKey.handle)
        self.SetFocus()
        self.PopupMenu(self._contextMenu, pos)

    def OnNewKey(self, event):
        self.GetTopLevelParent().OnNewKey(event)

    def OnEditKey(self, event):
        self.GetTopLevelParent().OnEditKey(event)

    def _initKeys(self):
        self._selectedKeyHandle = None

    def _updateScrollbars(self):
        self._updateKeys()
        self.SetScrollRate(self._scrollUnit.width, self._scrollUnit.height)
        self.SetVirtualSize(self._scroll)

    def _getContentSize(self):
        """
        Return, in logical units, the max height and width of the content.
        """
        return Size(200, 200)

    def _getScale(self, rect):
        # if scaled, scale is a ratio of content size to rect size
        # otherwise, scale is based on the width of the letter 'W'
        # in the current system font.
        if self._displayMode == DISPLAY_MODE_DYNAMIC_RESIZE:
            contentSize = self._getContentSize()
            scale = rect.width / contentSize.width
            if contentSize.height * scale <= rect.height:
                return scale
            return rect.height / contentSize.height
        else:
#           dc = wx.WindowDC(self)
#           (w, h) = dc.GetTextExtent('W')
#           return w
            return 25

    def _getDrawingArea(self):
        """
        Return a Rect encompassing the allowable drawing area of the current client window,
        in device units.
        """
        drawingArea = Rect(*self.GetClientRect())
        drawingArea.Deflate(self._border, self._border)
        return drawingArea

    def _getContentArea(self):
        """
        Based on the content size, in logical units, return, in device units,
        the rectangle encompassing the extents of the content to be drawn.
        """
        drawingArea = self._getDrawingArea()
        scale = self._getScale(drawingArea)
        contentSize = self._getContentSize() * scale
        contentArea = Rect(drawingArea.x, drawingArea.y, contentSize.width, contentSize.height)
        contentArea = contentArea.CenterIn(drawingArea)
        return contentArea


    def _refreshKey(self, displayKey):
        """
        Calculate the appropriate region of the screen to refresh based
        on the given displayKey.
        """
        refreshRect = Rect(*displayKey.scaled)
        refreshRect.Inflate(2, 2)
        self.RefreshRect(refreshRect.Get())

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
        drawingArea = self._getDrawingArea()
        self._scroll.width = self._scroll.height = 0
        self._scrollUnit = drawingArea.size
        scale = self._getScale(drawingArea)

        if self._displayMode == DISPLAY_MODE_DYNAMIC_RESIZE:
            contentArea = self._getContentArea()
            for displayKey in self._displayKeys.values():
                displayKey.scaled = displayKey.unscaled * scale
                displayKey.scaled.Offset(contentArea.origin)
                displayKey.labelRect = Rect(*displayKey.unscaled)
                displayKey.labelRect.Deflate(0.2, 0.2)
                displayKey.labelRect *= scale
                displayKey.labelRect.Offset(contentArea.origin)
            self._fontSize = scale * 0.37

        else:
            maxWidth = drawingArea.width / scale
            origin = Point(0, 0)
            for displayKeyHandle in self._orderedKeyHandles:
                displayKey = self._displayKeys[displayKeyHandle]
                if origin.x + self._keySize.width > maxWidth:
                    origin.x = 0
                    origin.y += self._keySize.height + self._keySpacing.height
                displayKey.unscaled.x = origin.x
                displayKey.unscaled.y = origin.y
                displayKey.scaled = displayKey.unscaled * scale
                self._scroll.width = max(self._scroll.width, displayKey.scaled.x + displayKey.scaled.width)
                self._scroll.height = max(self._scroll.height, displayKey.scaled.y + displayKey.scaled.height)
                displayKey.scaled.Offset(drawingArea.origin)
                displayKey.labelRect = Rect(*displayKey.unscaled)
                displayKey.labelRect.Deflate(0.2, 0.2)
                displayKey.labelRect *= scale
                displayKey.labelRect.Offset(drawingArea.origin)
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
            displayKey = self._hitTest(event.GetPosition())
            if displayKey is not None:
                self._tooltip.SetTip("\n%s" % displayKey.handle)
                self._tooltip.Enable(True)
            else:
                self._tooltip.Enable(False)

        elif event.LeftUp():
            displayKey = self._hitTest(event.GetPosition())
            if displayKey is not None:
                self._selectKey(displayKey.handle)
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
                displayKey = self._hitTest(self._dragStart)
                if displayKey is not None:
                    data = wx.CustomDataObject('sourcekey handle')
                    data.SetData(cPickle.dumps(displayKey.sourceHandle))
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
        for displayKey in self._displayKeys.values():
            if displayKey.scaled.Contains(point):
                return displayKey
        return None

    def _drawKeys(self, dc):
        blackPen = wx.Pen('black')
        whiteBrush = wx.Brush('white')

        # set the font
        self.font = wx.Font(self._fontSize, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL,
                       wx.FONTWEIGHT_BOLD, False, 'Arial Rounded MT Bold')
        dc.SetFont(self.font)

        for displayKey in self._displayKeys.values():

            # draw key shadow
            shadowRect = Rect(*displayKey.scaled)
            shadowRect.OffsetXY(1, 1)
            dc.SetPen(wx.Pen('light grey', 3.5))
            dc.DrawRoundedRectangleRect(shadowRect.Get(), -.075)

            # handle selections
            if self._isKeySelected(displayKey.handle):
                if self.FindFocus() == self:
                    # TODO: Generalize this magic number from system settings.
                    #       Currently is Mac selection blue.
                    dc.SetPen(wx.Pen('#3e75d6', 2))
                else:
                    dc.SetPen(wx.Pen('dark grey', 2))
                dc.SetBrush(wx.Brush('light grey'))
            else:
                dc.SetPen(blackPen)
                dc.SetBrush(whiteBrush)

            # draw key outline
            dc.DrawRoundedRectangleRect(displayKey.scaled.Get(), -.075)

            # draw label
            self._drawLabels(dc, displayKey.labelRect, displayKey)

    def _getLabels(self, displayKey):
        if displayKey is not None and displayKey.handle is not None:
            sourceKey = Model.sourcekeys[displayKey.handle]
            if sourceKey is not None:
                return sourceKey.labels
            return None

    def _drawLabels(self, dc, labelRect, displayKey):
        labels = self._getLabels(displayKey)
        if labels is not None:
            if labels.has_key('TopLeft'):
                self._drawSingleLabel(dc, labelRect, labels['TopLeft'],
                                      wx.ALIGN_LEFT|wx.ALIGN_TOP)
            if labels.has_key('BottomLeft'):
                self._drawSingleLabel(dc, labelRect, labels['BottomLeft'],
                                      wx.ALIGN_LEFT|wx.ALIGN_BOTTOM)
            if labels.has_key('TopRight'):
                self._drawSingleLabel(dc, labelRect, labels['TopRight'],
                                      wx.ALIGN_RIGHT|wx.ALIGN_TOP)
            if labels.has_key('BottomRight'):
                self._drawSingleLabel(dc, labelRect, labels['BottomRight'],
                                      wx.ALIGN_RIGHT|wx.ALIGN_BOTTOM)

    def _drawSingleLabel(self, dc, labelRect, label, position):
        (width, height) = dc.GetTextExtent(label)
        lines = []
        if width > labelRect.width:
            words = label.split()
            current = []
            for word in words:
                current.append(word)
                (width, height, dummy, dummy) = self.GetFullTextExtent(" ".join(current), self.font)
                if width > labelRect.width:
                    del current[-1]
                    lines.append(" ".join(current))
                    current = [word]

            # pick up the last line of text
            lines.append(" ".join(current))
            label = "\n".join(lines)
        else:
            lines.append(label)
        self._drawLabelLines(dc, lines, labelRect, position)
#       dc.DrawLabel(label, labelRect.Get(), position)

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

    def _drawLabelLines(self, dc, lines, rect, alignment):

        # find the text position
        text = "\n".join(lines)
        (widthText, heightText, heightLine) = dc.GetMultiLineTextExtent(text, self.font)

        width = widthText
        height = heightText

        x = y = None
        if (alignment & wx.ALIGN_RIGHT):
            x = rect.GetRight() - width
        elif (alignment & wx.ALIGN_CENTRE_HORIZONTAL):
            x = (rect.GetLeft() + rect.GetRight() + 1 - width) / 2
        else: # alignment & wx.ALIGN_LEFT
            x = rect.GetLeft()

        if (alignment & wx.ALIGN_BOTTOM):
            y = rect.GetBottom() - height
        elif (alignment & wx.ALIGN_CENTRE_VERTICAL):
            y = (rect.GetTop() + rect.GetBottom() + 1 - height) / 2
        else: # alignment & wx.ALIGN_TOP
            y = rect.GetTop()

        dc.SetPen(wx.Pen('red'))
        dc.DrawRectangle(*wx.Rect(x, y, widthText, heightText))
        dc.SetPen(wx.Pen('black'))

        # split the string into lines and draw each of them separately
        curLine = ''
        for line in lines:
            xRealStart = x;

            if len(line) is not 0:
                # NB: can't test for !(alignment & wx.ALIGN_LEFT) because
                #     wx.ALIGN_LEFT is 0
                if (alignment & (wx.ALIGN_RIGHT | wx.ALIGN_CENTRE_HORIZONTAL)):
                    (widthLine, dummy, dummy, dummy) = dc.GetFullTextExtent(line, self.font)

                    if (alignment & wx.ALIGN_RIGHT):
                        xRealStart += width - widthLine
                    else: # if (alignment & wx.ALIGN_CENTRE_HORIZONTAL):
                        xRealStart += (width - widthLine) / 2
                #else: left aligned, nothing to do

                dc.DrawText(line, xRealStart, y)

            y += heightLine

        # return bounding rect if requested
#       if (rectBounding):
#           *rectBounding = wx.Rect(x, y - heightText, widthText, heightText)
#
#       CalcBoundingBox(x0, y0)
#       CalcBoundingBox(x0 + width0, y0 + height)


def main():
    app = wx.PySimpleApp()
    frame = wx.Frame(None, -1, 'keydisplay')
    pane = KeyDisplayPane(frame, displayMode=DISPLAY_MODE_WRAPPED, border=10)
    pane._getDrawingArea()

if __name__ == '__main__':
    main()
