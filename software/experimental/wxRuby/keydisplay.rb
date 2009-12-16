require 'wx'

require 'utils'
require 'model'
require 'notifications'
require 'displaykey'


$DRAG_MODE_NONE     = 0
$DRAG_MODE_START    = 1
$DRAG_MODE_DRAGGING = 2

$DISPLAY_MODE_DYNAMIC_RESIZE = 0
$DISPLAY_MODE_WRAPPED        = 1

class KeyDisplayPane < Wx::ScrolledWindow

    def initialize(parent, displayMode, border)
        super(parent)
        @displayKeys = {}
        @orderedKeyHandles = []
        @keySize = Size.new(1.8, 1.8)
        @keySpacing = Size.new(0.2, 0.2)
        @border = border
        @selectedKeyHandle = nil
        @displayMode = displayMode
        @scroll = Wx::Size.new(0, 0)
        @scrollUnit = Wx::Size.new(0, 0)
        @tooltip = Wx::ToolTip.new("")
        @dragStart = nil
        @dragMode = $DRAG_MODE_NONE
        @fontSize = 10
        @font = nil
        evt_paint()        {|event| OnPaint(event)}
        evt_size()         {|event| OnSize(event)}
        evt_mouse_events() {|event| OnMouse(event)}
        evt_char()         {|event| OnChar(event)}
        evt_kill_focus()   {|event| OnKillFocus(event)}
        evt_set_focus()    {|event| OnSetFocus(event)}
        tool_tip = @tooltip
        set_scroll_rate(1, 1)
        createContextMenu()
    end

    def createContextMenu()
        @contextMenu = Wx::Menu.new
        item = @contextMenu.append(-1, "New Key...")
        evt_menu(item, :OnNewKey)
        @contextMenu.append_separator
        item = @contextMenu.append(-1, "Edit Key...")
        evt_menu(item, :OnEditKey)
        evt_context_menu() {|event| OnContextMenu(event)}
    end

    def OnContextMenu(event)
        pos = event.position
        pos = screen_to_client(pos)
        displayKey = _hitTest(pos)
        if displayKey != nil
            _selectKey(displayKey.handle)
        end
        set_focus
        popup_menu(@contextMenu, pos)
    end

    def OnNewKey(event)
        top_level_parent.OnNewKey(event)
    end

    def OnEditKey(event)
        top_level_parent.OnEditKey(event)
    end

    def _initKeys()
        @selectedKeyHandle = nil
    end

    def _updateScrollbars()
        _updateKeys()
        set_scroll_rate(@scrollUnit.width.to_i, @scrollUnit.height.to_i)
        set_virtual_size(@scroll)
    end

    def _getContentSize()
        #  Return, in logical units, the max height and width of the content.
        return Size.new(200, 200)
    end

    def _getScale(rect)
        # if scaled, scale is a ratio of content size to rect size
        # otherwise, scale is based on the width of the letter 'W'
        # in the current system font.
        if @displayMode == $DISPLAY_MODE_DYNAMIC_RESIZE
            contentSize = _getContentSize
            scale = rect.width / contentSize.width
            if contentSize.height * scale <= rect.height
                return scale
            end
            return rect.height / contentSize.height
        else
            #           dc = Wx::WindowDC
            #           (w, h) = dc.GetTextExtent('W')
            #           return w
            return 25
        end
    end

    # Return a Rect encompassing the allowable drawing area of the current client window,
    # in device units.
    def _getDrawingArea()
        drawingArea = Rect.new_with_rect(client_rect)
        drawingArea.Deflate(@border, @border)
        return drawingArea
    end

    # Based on the content size, in logical units, return, in device units,
    # the rectangle encompassing the extents of the content to be drawn.
    def _getContentArea()
        drawingArea = _getDrawingArea()
        scale = _getScale(drawingArea)
        contentSize = _getContentSize() * scale
        contentArea = Rect.new(drawingArea.x, drawingArea.y, contentSize.width, contentSize.height)
        contentArea = contentArea.CenterIn(drawingArea)
        return contentArea
    end


    # Calculate the appropriate region of the screen to refresh based
    # on the given displayKey.
    def _refreshKey(displayKey)
        refreshRect = Rect.new_with_rect(displayKey.scaled)
        refreshRect.Inflate(2, 2)
        refresh_rect(refreshRect.to_wxRect)
    end

    def _selectKey(displayKeyHandle)
        if not _isKeySelected(displayKeyHandle)
#           $stderr.puts "selectKey: .#{displayKeyHandle}. selected: .#{@selectedKeyHandle}."

            # de-select existing selection
            if @selectedKeyHandle != nil
                displayKey = @displayKeys[@selectedKeyHandle]
                @selectedKeyHandle = nil
                _refreshKey(displayKey);
            end

            # select new key
            if displayKeyHandle != nil
                @selectedKeyHandle = displayKeyHandle
                displayKey = @displayKeys[@selectedKeyHandle]
                _refreshKey(displayKey)
                KeyUpdateNotification.notify(displayKeyHandle)
            end
        end
    end

    def _isKeySelected(displayKeyHandle)
        return ((@selectedKeyHandle != nil) and (@selectedKeyHandle == displayKeyHandle))
    end

    def GetSelectedKeyHandle()
        return @selectedKeyHandle
    end

    # Adjust position and scale of each display key based on current display rect.
    def _updateKeys()

        drawingArea = _getDrawingArea
        @scroll.width = @scroll.height = 0
        @scrollUnit = drawingArea.size
        scale = _getScale(drawingArea)

        if @displayMode == $DISPLAY_MODE_DYNAMIC_RESIZE
            contentArea = _getContentArea
            @displayKeys.each_value do |displayKey|
                displayKey.scaled = displayKey.unscaled * scale
                displayKey.scaled.Offset(contentArea.origin)
                displayKey.labelRect = Rect.new_with_rect(displayKey.unscaled)
                displayKey.labelRect.Deflate(0.2, 0.2)
                displayKey.labelRect *= scale
                displayKey.labelRect.Offset(contentArea.origin)
            end
            @fontSize = scale * 0.37
        else
            maxWidth = drawingArea.width / scale
            origin = Point.new(0, 0)
            @orderedKeyHandles.each do |displayKeyHandle|
                displayKey = @displayKeys[displayKeyHandle]
                if origin.x + @keySize.width > maxWidth
                    origin.x = 0
                    origin.y += @keySize.height + @keySpacing.height
                end
                displayKey.unscaled.x = origin.x
                displayKey.unscaled.y = origin.y
                displayKey.scaled = displayKey.unscaled * scale
                @scroll.width = [@scroll.width, displayKey.scaled.x + displayKey.scaled.width].max.to_i
                @scroll.height = [@scroll.height, displayKey.scaled.y + displayKey.scaled.height].max.to_i
                displayKey.scaled.Offset(drawingArea.origin)
                displayKey.labelRect = Rect.new_with_rect(displayKey.unscaled)
                displayKey.labelRect.Deflate(0.2, 0.2)
                displayKey.labelRect *= scale
                displayKey.labelRect.Offset(drawingArea.origin)
                origin.x += @keySize.width + @keySpacing.width
                @scrollUnit.width = [@scrollUnit.width, displayKey.scaled.width].min.to_i
                @scrollUnit.height = [@scrollUnit.height, displayKey.scaled.height].min.to_i
            end
            @scroll.width  += @border * 2
            @scroll.height += @border * 2
            @scrollUnit.width  += @keySpacing.width  * scale
            @scrollUnit.height += @keySpacing.height * scale
        end
    end

    def OnSize(event)
        _updateScrollbars()
        refresh()
    end

    def OnMouse(event)
        if event.moving()
           displayKey = self._hitTest(event.get_position())
           if displayKey != nil
               @tooltip.set_tip("\n%s" % displayKey.handle)
               Wx::ToolTip.enable(true)
           else
               Wx::ToolTip.enable(false)
           end

        elsif event.left_up()
           displayKey = self._hitTest(event.get_position())
           if displayKey != nil
               self._selectKey(displayKey.handle)
           end
           @dragMode = $DRAG_MODE_NONE

        elsif event.left_down()
           @dragStart = event.get_position()
           @dragMode = $DRAG_MODE_START

        elsif event.dragging() and @dragMode != $DRAG_MODE_NONE
           if @dragMode == $DRAG_MODE_START
               # are we dragging yet?
               tolerance = 2
               dx = (event.get_position().x - @dragStart.x).abs
               dy = (event.get_position().y - @dragStart.y).abs
               if dx <= tolerance and dy <= tolerance
                   return
               end

               # start the drag
               @dragMode = $DRAG_MODE_DRAGGING
               displayKey = _hitTest(@dragStart)
               if displayKey != nil
                   data = Wx::CustomDataObject.new(Wx::DataFormat.new('sourcekey handle'))
#                  data.set_data(cPickle.dumps(displayKey.sourceHandle))
                   txt = Marshal.dump(displayKey.source_handle)
                   data.set_data(txt.size, txt)
                   dropSource = Wx::DropSource.new
                   dropSource.set_data(data)
                   result = dropSource.do_drag_drop(Wx::Drag_AllowMove)
                   if result == Wx::DragMove
                       pass
                   end
               end
           end
        end
        event.skip
    end

    def OnChar(event)
        if @selectedKeyHandle == nil
           selectKey(@displayKeys.keys[0])
        end
        displayKey = @displayKeys[@selectedKeyHandle]
        pos = nil
        case code = event.get_key_code()
        when Wx::K_LEFT
            pos = Point.new(displayKey.unscaled.x - @keySpacing.width - 1,
                            displayKey.unscaled.y)
        when Wx::K_RIGHT
           pos = Point.new(displayKey.unscaled.x + displayKey.unscaled.width + @keySpacing.width + 1,
                           displayKey.unscaled.y)
        when Wx::K_UP
           pos = Point.new(displayKey.unscaled.x,
                           displayKey.unscaled.y - @keySpacing.height - 1)
        when Wx::K_DOWN
           pos = Point.new(displayKey.unscaled.x,
                           displayKey.unscaled.y + displayKey.unscaled.height + @keySpacing.height + 1)
        else
           event.Skip()
           return
        end

        selectKeyHandle = nil
        @displayKeys.each do |displayKeyHandle, displayKey|
           if displayKey.unscaled.Contains(pos)
               selectKeyHandle = displayKeyHandle
               break
           end
        end
        if selectKeyHandle != nil
           _selectKey(selectKeyHandle)
        end
    end

    # Given a point in device coordinates, return a handle to the display
    # key that contains the point, or nil if no corresponding display key is
    # found
    def _hitTest(point)
        point = calc_unscrolled_position(point)
        @displayKeys.each_value do |displayKey|
            if displayKey.scaled.Contains(point)
                return displayKey
            end
        end
        return nil
    end

    def _drawKeys(dc)
        blackPen = Wx::Pen.new('black')
        whiteBrush = Wx::Brush.new('white', Wx::SOLID)

        @displayKeys.each_value do |displayKey|
            # draw key shadow
            shadowRect = Rect.new_with_rect(displayKey.scaled)
            shadowRect.OffsetXY(1, 1)
            dc.set_pen(Wx::Pen.new('light grey', 3))
            dc.draw_rounded_rectangle(shadowRect.x.to_i, shadowRect.y.to_i,
                                      shadowRect.width.to_i, shadowRect.height.to_i, -0.075)

            # handle selections
            if _isKeySelected(displayKey.handle)
                $stderr.puts "I've got focus: #{Wx::Window.find_focus()}"
                if Wx::Window.find_focus() == self
                    # TODO: Generalize this magic number from system settings.
                    #       Currently is Mac selection blue.
                    dc.set_pen(Wx::Pen.new('#3e75d6', 2))
                else
                    dc.set_pen(Wx::Pen.new('dark grey', 2))
                end
                dc.set_brush(Wx::Brush.new('light grey', Wx::SOLID))
            else
                dc.set_pen(blackPen)
                dc.set_brush(whiteBrush)
            end

            # draw key outline
            dc.draw_rounded_rectangle(displayKey.scaled.x.to_i, displayKey.scaled.y.to_i,
                                      displayKey.scaled.width.to_i, displayKey.scaled.height.to_i,
                                      -0.075)

            # draw label
            _drawLabels(dc, displayKey.labelRect, displayKey)
        end
    end

    def _getLabels(displayKey)
        if displayKey != nil and displayKey.handle != nil
            sourceKey = Model.sourcekeys[displayKey.handle]
            if sourceKey != nil
                return sourceKey.labels
            end
            return nil
        end
    end

    def _drawLabels(dc, labelRect, displayKey)
        labels = self._getLabels(displayKey)
        if labels != nil
            if labels.has_key?('TopLeft')
                _drawSingleLabel(dc, labelRect, labels['TopLeft'],
                                 Wx::ALIGN_LEFT|Wx::ALIGN_TOP)
            end
            if labels.has_key?('BottomLeft')
                _drawSingleLabel(dc, labelRect, labels['BottomLeft'],
                                 Wx::ALIGN_LEFT|Wx::ALIGN_BOTTOM)
            end
            if labels.has_key?('TopRight')
                _drawSingleLabel(dc, labelRect, labels['TopRight'],
                                 Wx::ALIGN_RIGHT|Wx::ALIGN_TOP)
            end
            if labels.has_key?('BottomRight')
                _drawSingleLabel(dc, labelRect, labels['BottomRight'],
                                 Wx::ALIGN_RIGHT|Wx::ALIGN_BOTTOM)
            end
        end
    end

    def wrap_text_to_rect(rect, text, font)
        (width, height, dummy, dummy) = get_text_extent(text, font)
        lines = []
        totalHeight = 0
        if width > rect.width
            words = text.split()
            current = []
            words.each do |word|
                current.push(word)
                (width, height, dummy, dummy) = get_text_extent(current.join(" "), font)
                if width > rect.width
                    current.pop
                    lines.push(current.join(" "))
                    totalHeight += height
                    current = [word]
                end
            end

            # pick up the last line of text
            lines.push(current.join(" "))
            totalHeight += height
#           text = lines.join("\n")
        else
            lines.push(text)
        end
        return nil if totalHeight > rect.height
        return lines
    end

    def _drawSingleLabel(dc, labelRect, label, position)
        @font = Wx::Font.new(@fontSize.to_i, Wx::FONTFAMILY_DEFAULT, Wx::FONTSTYLE_NORMAL,
#                            Wx::FONTWEIGHT_BOLD, false, 'Arial Rounded MT Bold',
                             Wx::FONTWEIGHT_BOLD, false, 'Osaka',
                             Wx::FONTENCODING_DEFAULT)
        font = @font
        lines = wrap_text_to_rect(labelRect, label, font)
        while lines == nil
            font.point_size = font.point_size - 1
            lines = wrap_text_to_rect(labelRect, label, font)
        end
        _drawLabelLines(dc, lines, labelRect, position, font)
    end

    def OnPaint(event)
        paint do |dc|
            _drawKeys(dc)
        end
    end

    def OnKillFocus(event)
        refresh()
    end

    def OnSetFocus(event)
        $stderr.puts "OnSetFocus #{self} #{@selectedKeyHandle}"
        if @selectedKeyHandle
            KeyUpdateNotification.notify(@selectedKeyHandle)
            refresh()
        end
    end

    def _drawLabelLines(dc, lines, rect, alignment, font)

        dc.font = font

        # find the text position
        text = lines.join("\n")
        (widthText, heightText, heightLine) = dc.get_multi_line_text_extent(text, font)

        width = widthText
        height = heightText

        x = y = nil
        if ((alignment & Wx::ALIGN_RIGHT) != 0)
            x = rect.right - width
        elsif ((alignment & Wx::ALIGN_CENTRE_HORIZONTAL) != 0)
            x = (rect.left + rect.right + 1 - width) / 2
        else  # alignment & Wx::ALIGN_LEFT
            x = rect.left
        end

        if ((alignment & Wx::ALIGN_BOTTOM) != 0)
            y = rect.bottom - height
        elsif ((alignment & Wx::ALIGN_CENTRE_VERTICAL != 0))
            y = (rect.top + rect.bottom + 1 - height) / 2
        else  # alignment & Wx::ALIGN_TOP
            y = rect.top
        end

#       dc.set_pen(Wx::Pen.new('red'))
#       dc.draw_rectangle(x.to_i, y.to_i, widthText.to_i, heightText.to_i)
        dc.set_pen(Wx::Pen.new('black'))

        # split the string into lines and draw each of them separately
        curLine = ''
        lines.each do |line|
            xRealStart = x;

            if !line.empty?
                # NB: can't test for !(alignment & Wx::ALIGN_LEFT) because
                #     Wx::ALIGN_LEFT is 0
                if ((alignment & (Wx::ALIGN_RIGHT | Wx::ALIGN_CENTRE_HORIZONTAL)) != 0)
                    (widthLine, dummy, dummy, dummy) = dc.get_text_extent(line, font)

                    if ((alignment & Wx::ALIGN_RIGHT != 0))
                        xRealStart += width - widthLine
                    else # if (alignment & Wx::ALIGN_CENTRE_HORIZONTAL)
                        xRealStart += (width - widthLine) / 2
                    end
                #else # left aligned, nothing to do
                end

                dc.draw_text(line, xRealStart.to_i, y.to_i)
            end

            y += heightLine
        end

        # return bounding rect if requested
#       if (rectBounding)
#           *rectBounding = Wx::Rect(x, y - heightText, widthText, heightText)
#
#       CalcBoundingBox(x0, y0)
#       CalcBoundingBox(x0 + width0, y0 + height)

    end
end

if $0 == __FILE__
    Wx::App.run do
        Model.StaticInit()
        frame = Wx::Frame.new(nil, -1, 'keydisplay')
        pane = KeyDisplayPane.new(frame, $DISPLAY_MODE_WRAPPED, 10)
        pane._getDrawingArea
    end
end
