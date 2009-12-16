#
#  DestPage.rb
#  Keys.rb
#
#  Created by David on 6/19/08.
#  Copyright (c) 2008 Red Goat Software. All rights reserved.
#

require 'osx/cocoa'
require 'KeyDisplayPage'
require 'DestDisplayKey'
require 'utils'

class DestPage <  KeyDisplayPage

 def init(parent, keymap)
   NSLog("DestPage::init(#{parent}, #{keymap}))")
   super(parent, $DISPLAY_MODE_DYNAMIC_RESIZE, 10)
   @kb = Model.keyboard
   @keymap = keymap
#     ModelChangeNotification.add_observer(self.method(:NotifyModelChange))
#     self.background_colour = Wx::SystemSettings.get_colour(Wx::SYS_COLOUR_BTNFACE)
#     dt = DestDropTarget.new(self)
#     set_drop_target(dt)
   return self
 end
  
 def _initKeys()
   #     @keySpacing = Wx::Size.new(@kb.layout.spacing.to_i, @kb.layout.spacing.to_i)
   @displayKeys = {}
   selectedKey = nil
   @kb.layout.rows.each do |row|
     NSLog("row = #{row}")
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
#     _selectKey(selectedKey)
 end

 def _getContentSize()
   return @kb.maxSize
 end

end
