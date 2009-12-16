#import sys
#
#import wx
#import wx.lib.colourdb
#
#import data
#from util import Point, Rect
#from splitter import SplitterWindow
#from keydisplay import KeyDisplayPane, DisplayKey, DISPLAY_MODE_WRAPPED
#from notifications import KeyUpdateNotification, CategoryChangeNotification
#from model import Model

require 'wx'
require 'splitter'
require 'keydisplay'
require 'notifications'

class SourcePane < $SplitterWindow

    def initialize(parent)
        super(parent, :style => (Wx::SP_LIVE_UPDATE|Wx::SP_3D))
        set_sash_gravity(0.5)
        left = CategoryPane.new(self)
        right = SelectorPane.new(self)
        left.hide()
        init(right)
        self.minimum_pane_size = 200
#       set_minimum_pane_size(10)
        split_vertically(left, right, 200)
    end
end


class CategoryPane < Wx::Panel

    def initialize(parent)
        super(parent)
        @content = Wx::TreeCtrl.new(self,
                                    :pos => Wx::DEFAULT_POSITION,
                                    :size => Wx::DEFAULT_SIZE,
                                    :style => Wx::TR_DEFAULT_STYLE|Wx::NO_BORDER|Wx::TR_HIDE_ROOT)
        evt_tree_sel_changed(@content) {|event| OnSelChanged(event)}
        root = @content.add_root('root')

        Model.categories.each_value do |category|
             @content.append_item(root, category.name)
        end
        @content.set_background_colour(Wx::Colour.new('#e7edf6'))

        sizer = Wx::BoxSizer.new(Wx::VERTICAL)
        sizer.add(@content, 1, Wx::EXPAND)
        set_sizer(sizer)
        fit()
    end

    def OnSelChanged(event)
        category = @content.get_item_text(event.get_item())
        CategoryChangeNotification.notify(category)
    end
end


class SelectorPane < KeyDisplayPane

    def initialize(parent)
        super(parent, $DISPLAY_MODE_WRAPPED, 10)
        @category = nil
        CategoryChangeNotification.add_observer(self.method(:NotifyCategoryChange))
        color = Wx::SystemSettings.get_colour(Wx::SYS_COLOUR_WINDOW)
        set_background_colour(color)
    end

    def NotifyCategoryChange(notification)
        @category = Model.categories[notification.category]
        _initKeys()
        refresh()
    end

    def _initKeys
        super
        @displayKeys.clear()
        @orderedKeyHandles = @category.keyHandles
        for keyHandle in @category.keyHandles
            if not Model.sourcekeys.has_key?(keyHandle)
                raise "Unknown key '#{keyHandle}' in category '#{@category.name}'"
            end
            sourceKey = Model.sourcekeys[keyHandle]
            rect = Rect.new(0, 0, @keySize.width, @keySize.height)
            @displayKeys[keyHandle] = DisplayKey.new(keyHandle, rect)
        end
        _updateKeys()
        _selectKey(@orderedKeyHandles[0])
        _updateScrollbars()
    end

    def _getLabel(displayKey)
        if Model.sourcekeys.has_key?(displayKey.handle)
            sourceKey = Model.sourcekeys[displayKey.handle]
            if sourceKey.labels.has_key?('BottomLeft')
                return sourceKey.labels['BottomLeft']
            end
            if sourceKey.labels.has_key?('TopLeft')
                return sourceKey.labels['TopLeft']
            end
        end
        return ''
    end
end


if $0 == __FILE__
    require 'model'
    Wx::App.run do
        Model.StaticInit()
        frame = Wx::Frame.new(nil, -1, 'source')
        pane = SourcePane.new(frame)
        frame.show()
    end
end
