#import wx
#import cPickle
#
#from util import Rect, Point, say
#from notifications import KeyUpdateNotification, ModelChangeNotification, \
#                          LayerChangeNotification
#from keydisplay import KeyDisplayPane, DisplayKey, DISPLAY_MODE_DYNAMIC_RESIZE
#from keyboard import KeyRef
#from model import Model
#
require 'keydisplay'

class DestDisplayKey < DisplayKey

    attr_reader :location

    def initialize(location, sourcekeyHandle, unscaled)
        super(sourcekeyHandle, unscaled)
        @location = location
    end

    def display_handle
        return @location
    end

end

class DestDropTarget < Wx::DropTarget

    def initialize(parent)
        super(nil)  # TODO: investigate in wxRuby why this requires an argument.
        @parent = parent
        @data = Wx::CustomDataObject.new(Wx::DataFormat.new('sourcekey handle'))
        data_object = @data
    end

#   def OnDrop(x, y)
#       dlg = Wx::MessageDialog(@parent, "Dropped at (%d, %d)" % (x, y),
#                              "Dropping", Wx::OK | Wx::ICON_INFORMATION)
#       dlg.ShowModal()
#       dlg.Destroy()
#   end

    def OnData(x, y, default)
        data = nil
        GetData()
        sourceHandle = cPickle.loads(@data.GetData())
        @parent.DoDrop(x, y, sourceHandle)
        return default
    end
end

class DestPane < Wx::Notebook

    def initialize(parent)
        super(parent)
        parent.background_colour = Wx::SystemSettings.get_colour(Wx::SYS_COLOUR_BTNFACE)

        LayerChangeNotification.add_observer(self.method(:NotifyLayerChange))

        for keymap in Model.keyboard.maps
            page = DestPage.new(self, keymap)
            add_page(page, keymap.ids.last, Wx::ID_ANY)
        end

        set_selection(0)
    end

    def NotifyLayerChange(notification)
        layer = notification.layer
        index = 0
        Model.keyboard.maps do |keymap|
            if keymap.ids.last == layer
                break
            end
            index += 1
        end
        set_selection(index)
        refresh()
    end
end

class DestPage < KeyDisplayPane

    def initialize(parent, keymap)
        @kb = Model.keyboard
        super(parent, $DISPLAY_MODE_DYNAMIC_RESIZE, 10)
        @keymap = keymap
        ModelChangeNotification.add_observer(self.method(:NotifyModelChange))
        self.background_colour = Wx::SystemSettings.get_colour(Wx::SYS_COLOUR_BTNFACE)
        dt = DestDropTarget.new(self)
        set_drop_target(dt)
    end

    def _initKeys()
        @keySpacing = Wx::Size.new(@kb.layout.spacing.to_i, @kb.layout.spacing.to_i)
        @displayKeys = {}
        selectedKey = nil
        @kb.layout.rows.each do |row|
            if row == nil
                next
            end
            row.keydefs.each do |keydef|
                if keydef.isNullKey
                    next
                end
                keyRect = Rect.new(keydef.origin.x, keydef.origin.y,
                                   keydef.size.width, keydef.size.height)
                location = keydef.location
                keyHandle = nil
                if @keymap and @keymap.keys.has_key?(location)
                    keyHandle = @keymap.keys[location].keyHandle
                end
                @displayKeys[location] = DestDisplayKey.new(location, keyHandle, keyRect)
                if selectedKey == nil
                    selectedKey = location
                end
            end
        end

        _updateKeys
        _selectKey(selectedKey)
    end

    def GetSelectedKeyHandle()
        if @selectedKeyHandle
            return @displayKeys[@selectedKeyHandle].sourceHandle
        end
    end

    def NotifyModelChange(notification)
        _initKeys
    end

    def DoDrop(x, y, sourceHandle)
        displayKey = _hitTest(Wx::Point(x, y))
        if not displayKey
            print "You missed"
            return
        end
        @keymap.keys[displayKey.location] = KeyRef(displayKey.location, sourceHandle)
        ModelChangeNotification(nil).notify()
    end

    def _getLabels(displayKey)
        if @keymap and @keymap.keys.has_key?(displayKey.location)
            keyref = @keymap.keys[displayKey.location]
            sourceKey = Model.sourcekeys[keyref.keyHandle]
            return sourceKey.labels
        end
        return nil
    end

    def _getContentSize()
        return @kb.maxSize
    end
end

if $0 == __FILE__
    require 'Model'
    Wx::App.run do
        Model.StaticInit()
        frame = Wx::Frame.new(nil, -1, 'dest')
        pane = DestPane.new(frame)
        frame.show()
    end
end


