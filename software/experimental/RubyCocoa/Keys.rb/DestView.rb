#
#  DestView.rb
#  Keys.rb
#
#  Created by David Whetstone on 6/19/08.
#  Copyright (c) 2008 RedGoat Software, Inc. All rights reserved.
#

require 'osx/cocoa'
include OSX

require 'DestPage'

class DestView <  OSX::NSTabView

  ib_outlets :test

  def awakeFromNib
    NSLog("DestView::awakeFromNib")

    for keymap in Model.keyboard.maps
      NSLog("keymap #{keymap}")
      tabItem = NSTabViewItem.alloc.initWithIdentifier(keymap)
      tabItem.setLabel(keymap.to_s)
      page = DestPage.alloc.init(self, keymap)
      page._initKeys()
      tabItem.setView(page)
      self.addTabViewItem(tabItem)
    end
  end

  def initWithFrame(frame)
    super_initWithFrame(frame)
    NSLog("DestView::initWithFrame(#{frame})")
    @test = 0
    return self
  end

end
