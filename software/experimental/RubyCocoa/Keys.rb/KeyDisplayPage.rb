#
#  KeyDisplayPage.rb
#  Keys.rb
#
#  Created by David on 6/19/08.
#  Copyright (c) 2008 Red Goat Software. All rights reserved.
#

require 'osx/cocoa'

require 'utils'
require 'model'
require 'notifications'
require 'displaykey'

$DISPLAY_MODE_DYNAMIC_RESIZE = 0
$DISPLAY_MODE_WRAPPED        = 1

class KeyDisplayPage <  OSX::NSView

  def init(parent, displayMode, border)
    NSLog("DestPage::init(#{parent}, #{displayMode})")
    @displayKeys = {}
    @orderedKeyHandles = []
    @keySize = Size.new(1.8, 1.8)
    @keySpacing = Size.new(0.2, 0.2)
    @border = border
    @selectedKeyHandle = nil
    @displayMode = displayMode
    @scroll = Size.new(0, 0)
    @scrollUnit = Size.new(0, 0)
    @dragStart = nil
    @dragMode = $DRAG_MODE_NONE
    @fontSize = 10
    @font = nil
    return self
  end
	
  def drawRect(rect)
    _drawKeys(rect)
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
        NSLog("scale = #{scale}")
        return scale
      end
      scale = rect.height / contentSize.height
      NSLog("scale = #{scale}")
      return scale
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
    drawingArea = Rect.new_with_nsrect(self.bounds())
    if drawingArea
      drawingArea.Deflate(@border, @border)
#      NSLog("drawingArea = #{drawingArea}")
    end
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
#        displayKey.scaled.y *= -1
#        displayKey.scaled.y -= drawingArea.height
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

  def _drawKeys(rect)

    _updateKeys()

    gc = NSGraphicsContext.currentContext
    gc.saveGraphicsState()

    drawingArea = _getDrawingArea
     r = NSRect.new(drawingArea.x, drawingArea.y, drawingArea.width, drawingArea.height)
    OSX::NSColor.blackColor().set()
    OSX::NSFrameRect(r)
    bounds = self.bounds()
    OSX::NSColor.redColor().set()
    OSX::NSFrameRect(bounds)


#    bounds = self.bounds()
    OSX::NSColor.blackColor().set()
#    OSX::NSBezierPath.fillRect_(bounds)


#		blackPen = Wx::Pen.new('black')
#		whiteBrush = Wx::Brush.new('white', Wx::SOLID)
#		
    @displayKeys.each_value do |displayKey|
#      NSLog("displayKey #{displayKey}")
      # draw key shadow
#			shadowRect = Rect.new_with_rect(displayKey.scaled)
#			shadowRect.OffsetXY(1, 1)
#			dc.set_pen(Wx::Pen.new('light grey', 3))
#			dc.draw_rounded_rectangle(shadowRect.x.to_i, shadowRect.y.to_i,
#																shadowRect.width.to_i, shadowRect.height.to_i, -0.075)
#			
      # handle selections
#			if _isKeySelected(displayKey.handle)
#				$stderr.puts "I've got focus: #{Wx::Window.find_focus()}"
#				if Wx::Window.find_focus() == self
#					# TODO: Generalize this magic number from system settings.
#					#       Currently is Mac selection blue.
#					dc.set_pen(Wx::Pen.new('#3e75d6', 2))
#				else
#					dc.set_pen(Wx::Pen.new('dark grey', 2))
#				end
#				dc.set_brush(Wx::Brush.new('light grey', Wx::SOLID))
#			else
#				dc.set_pen(blackPen)
#				dc.set_brush(whiteBrush)
#			end
#			
      # draw key outline
#       r = NSRect.new(displayKey.unscaled.x, displayKey.unscaled.y,
#                      displayKey.unscaled.width, displayKey.unscaled.height)
     r = NSRect.new(displayKey.scaled.x, displayKey.scaled.y,
                      displayKey.scaled.width, displayKey.scaled.height)
      OSX::NSFrameRect(r)

#      dc.draw_rounded_rectangle(displayKey.scaled.x.to_i, displayKey.scaled.y.to_i,
#                                displayKey.scaled.width.to_i, displayKey.scaled.height.to_i,
#                                -0.075)
			
      # draw label
#			_drawLabels(dc, displayKey.labelRect, displayKey)
    end

    gc.restoreGraphicsState()

  end

  def viewWillStartLiveResize()
    _updateKeys()
  end

  def isFlipped()
    return true
  end

end
