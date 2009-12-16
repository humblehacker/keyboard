#import wx
#import re
#
#from util import Rect, Point, say, Size
#from notifications import KeyUpdateNotification, ModelChangeNotification, \
#                          LayerChangeNotification
#from keydisplay import KeyDisplayPane, DisplayKey, DISPLAY_MODE_DYNAMIC_RESIZE, \
#                       DISPLAY_MODE_WRAPPED
#from model import Model, SourceKey, MacroKey
#from hid import Usage

require 'wx'
require 'keydisplay'

class NewKeyDropTarget < Wx::DropTarget

    def initialize(parent)
        super
        @parent = parent
        @data = Wx::TextDataObject()
        SetDataObject(@data)
    end

    def OnData(x, y, default)
        super
        actualData = @data.GetText()
        @parent.DoDrop(x, y, actualData)
        return default
    end
end


class TestPane < Wx::Panel

    def initialize(parent)
        super(parent)
#       Wx::Panel.initialize(parent, size=(200, 200))
        evt_paint() {|event| OnPaint(event)}
#       self.Bind(Wx::EVT_PAINT, self.OnPaint)
    end

    def OnPaint(event)
        dc = Wx::PaintDC(self)
        rect = GetClientRect()
        dc.SetPen(Wx::Pen('black'))
        dc.DrawRectangleRect(rect)
        dc.DrawLabel("#{self.class} (#{rect.width}, #{rect.height})",
                     rect.Get(), Wx::ALIGN_CENTER)
    end
end


class NewKeyPane < Wx::Panel

    attr_reader :cancelButton, :okButton

    def initialize(parent, keyHandle=nil)
        super

        @okButton = Wx::Button.new(self, Wx::ID_OK)
        @cancelButton = Wx::Button.new(self, Wx::ID_CANCEL)

        sourceKey = nil
        if keyHandle != nil
            sourceKey = Model.sourcekeys[keyHandle]
        else
            sourceKey = SourceKey.new(nil)
        end
#       assert(sourceKey != nil)

        dispPane  = DispPane.new(self, sourceKey)
        macroPane = MacroPane.new(self, sourceKey)
        modPane   = ModifierKeyPane.new(self)

        leftSizer = Wx::BoxSizer.new(Wx::VERTICAL)
        leftSizer.add(dispPane, 1, Wx::EXPAND)
        leftSizer.add(modPane,  1, Wx::EXPAND)

        upperSizer = Wx::BoxSizer.new(Wx::HORIZONTAL)
        upperSizer.add(leftSizer, 1, Wx::EXPAND)
        upperSizer.add(macroPane, 2, Wx::EXPAND)

        btnSizer = Wx::StdDialogButtonSizer.new()
        btnSizer.affirmative_button = @okButton
        btnSizer.cancel_button = @cancelButton
        btnSizer.realize()

        mainSizer = Wx::BoxSizer.new(Wx::VERTICAL)
        mainSizer.add(upperSizer, 1, Wx::EXPAND)
        mainSizer.add(btnSizer, 0, Wx::EXPAND|Wx::ALL, 10)
        set_sizer(mainSizer)

        mainSizer.fit(self)
        mainSizer.set_size_hints(self)
    end
end


class DispPane < KeyDisplayPane

    def initialize(parent, sourceKey)
        super(parent, $DISPLAY_MODE_DYNAMIC_RESIZE, 10)
        @sourceKey = sourceKey
        @dispKey = DisplayKey.new(sourceKey.handle, Rect.new(0, 0, 1.8, 1.8))
        @displayKeys = {sourceKey.handle => @dispKey}
        _updateKeys()
        _initKeys()
    end

    def _getContentSize
        return Size.new(1.8, 1.8)
    end

#   def OnPaint(self, event)
#       dc = Wx::PaintDC(self)
#       rect = self.GetClientRect()
#       dc.DrawRectangleRect(rect)
#       KeyDisplayPane.OnPaint(self, event)
end

class MacroPane < KeyDisplayPane

    def initialize(parent, sourceKey)
        super(parent, $DISPLAY_MODE_WRAPPED, 10)
        @displayKeys = {}
        _initKeys()
        evt_paint() {|event| OnPaint(event)}
        @keySize = Size.new(6.0, 2.5)
        @keySpacing = Size.new(0.2, 0.2)
        keyRect = Rect.new(0, 0, *@keySize)
        handle = nil
        if sourceKey.usage
            handle = sourceKey.usage.MakeHandle()
        elsif sourceKey.mode
            handle = "mode:%s" % sourceKey.mode
        elsif len(sourceKey.macro) > 0
            for (i, macroKey) in enumerate(sourceKey.macro)
                handle = macroKey.MakeHandle(i)
                @displayKeys[handle] = DisplayKey.new(handle, keyRect)
                @orderedKeyHandles.push(handle)
            end
            handle = nil
        end
        if handle != nil
            dispKey = DisplayKey.new(handle, keyRect)
            @displayKeys[handle] = dispKey
            @orderedKeyHandles.push(handle)
            _updateKeys()
        end
    end

    def _getLabels(displayKey)
        labels = {}
        print displayKey.handle
        keyInfo = displayKey.handle.split(':')
        if keyInfo[0] == 'usage'
            labels['TopLeft'] = "page: #{keyInfo[1]} id: #{keyInfo[2]}"
        elsif keyInfo[0] == 'mode'
            labels['TopLeft'] ="mode: #{keyInfo[1]}"
        elsif keyInfo[0] == 'macro'
            labels['BottomLeft'] = "modifiers: #{keyInfo[4]} "
            labels['TopLeft'] = "page: #{keyInfo[2]} id: #{keyInfo[3]}"
        elsif keyInfo[0] == 'm_usage'
            labels['TopLeft'] = "page: #{keyInfo[2]} id: #{keyInfo[3]}"
        else
            labels['BottomLeft'] = "?"
        end
        return labels
    end

    def OnPaint(event)
        paint do |dc|
            rect = get_client_rect()
            dc.draw_rectangle(rect.x.to_i, rect.y.to_i, rect.width.to_i, rect.height.to_i)
            super
        end
    end
end


class ModifierKeyPane < KeyDisplayPane

    def initialize(parent)
        super(parent, $DISPLAY_MODE_DYNAMIC_RESIZE, 0)
        _initKeys()
    end

    def _initKeys
        super
        @displayKeys = { 'left_shift'=>  DisplayKey.new('left_shift',  Rect.new(0.0, 0.0, 2.8, 1.8)),
                         'left_ctrl'=>   DisplayKey.new('left_ctrl',   Rect.new(0.0, 2.0, 2.8, 1.8)),
                         'left_alt'=>    DisplayKey.new('left_alt',    Rect.new(0.0, 4.0, 2.8, 1.8)),
                         'left_gui'=>    DisplayKey.new('left_gui',    Rect.new(0.0, 6.0, 2.8, 1.8)),
                         'right_shift'=> DisplayKey.new('right_shift', Rect.new(3.0, 0.0, 2.8, 1.8)),
                         'right_ctrl'=>  DisplayKey.new('right_ctrl',  Rect.new(3.0, 2.0, 2.8, 1.8)),
                         'right_alt'=>   DisplayKey.new('right_alt',   Rect.new(3.0, 4.0, 2.8, 1.8)),
                         'right_gui'=>   DisplayKey.new('right_gui',   Rect.new(3.0, 6.0, 2.8, 1.8)) }
        _updateKeys()
    end

    def _getContentSize
        return Size.new(6.0, 8.0)
    end
end

if $0 == __FILE__
    Wx::App.run do
        Model.StaticInit()
        frame = Wx::Frame.new(nil, -1, 'newkey')
        pane = NewKeyPane.new(frame)
        frame.show()
    end
end

