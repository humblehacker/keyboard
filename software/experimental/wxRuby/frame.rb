require 'rubygems'
require 'wx'

require 'model'
require 'notifications'
require 'splitter'
require 'source'
require 'dest'
require 'newkey'

class MainFrame < Wx::Frame

    def initialize()
        @initpos = 100
        super(nil, -1, "Remapper", :pos => [50,50], :size => [800,600])
#       @infoFrame = nil
        @statusbar = create_status_bar()
        @sourcePane = nil
        @destPane = nil
        @newKeyPane = nil
        create_toolbar()
        create_menubar()
        create_splitter()
        evt_left_dclick() {|event| on_double_click(event) }
        LayerChangeNotification.add_observer(self.method(:notify_layer_change))
        LayerChangeNotification.notify(Model.keyboard.maps[0].ids[-1])
        ModelChangeNotification.notify(nil)
    end

    def on_double_click(event)
        dlg = Wx::MessageDialog.new(:parent  => self,
                                    :message => "Double Click!",
                                    :title   => "Hey!",
                                    :style   => Wx::OK | Wx::ICON_INFORMATION)
        dlg.show_modal()
        dlg.destroy()
    end

    def create_toolbar
        toolbar = create_tool_bar();
        bmp = Wx::Bitmap.new("hand_point3.gif", Wx::BITMAP_TYPE_GIF)
        tool = toolbar.add_tool(-1, "The Finger", bmp)
        toolbar.realize()
    end

    def create_splitter
        @sp = $SplitterWindow.new(self, :style => Wx::SP_LIVE_UPDATE)
        @sourcePane = SourcePane.new(@sp)
#       @sourcePane = Wx::Panel.new(@sp)
        @destPane = DestPane.new(@sp)
#       @destPane = Wx::Panel.new(@sp)
        @sourcePane.hide()
        @sp.init(@destPane)
        @sp.split_horizontally(@sourcePane, @destPane, @initpos)
        if RUBY_PLATFORM =~ /darwin/
            # WORKAROUND: the position parameter passed to SplitVertically
            # (see SourcePane.__init__()) seems to be ignored.
#           @sourcePane.sash_position = 200
        end
    end

    def create_menubar
       # File menu
       fileMenu = Wx::Menu.new
       item = fileMenu.append(-1, "&New Key...")
       evt_menu(item, :OnNewKey)
       item = fileMenu.append(-1, "&Edit Key...")
       evt_menu(item, :OnEditKey)
       item = fileMenu.append(Wx::ID_ANY, "&Open...")
       item = fileMenu.append(Wx::ID_EXIT, "&Exit")
       item = fileMenu.append(Wx::ID_PREFERENCES, "&Preferences")

       evt_menu(item, :OnQuit)
       evt_menu(item, :OnOpen)
       evt_menu(item, :OnPrefs)

       # Help Menu
       helpMenu = Wx::Menu.new
       item = helpMenu.append(Wx::ID_HELP, "&Help")
       evt_menu(item, :OnHelp)
       ## this gets put in the App menu on OS-X
       item = helpMenu.append(Wx::ID_ABOUT, "&About", "More information About this program")
       evt_menu(item, :OnAbout)

       # View menu
       viewMenu = Wx::Menu.new
#      item = viewMenu.append(-1, "Show Info\tCtrl+I")
#      evt_menu(item, :OnShowInfo)
       item = viewMenu.append(-1, "Show Source pane")

       # Actions menu
       actionsMenu = Wx::Menu.new
       item = actionsMenu.append(-1, "Upload", "Upload changes to keyboard")
       item = actionsMenu.append(-1, "Download", "Download existing key maps from keyboard")
       item = actionsMenu.append(-1, "Reset", "Reset the keyboard to factory settings")

       # Layers menu
       layersMenu = Wx::Menu.new
       Model.keyboard.maps.each do |map|
           item = layersMenu.append_radio_item(-1, map.ids.last)
           evt_menu(item, :OnChangeLayer)
       end
       layersMenu.append_separator()
       item = layersMenu.append(-1, "New Layer")
       evt_menu(item, :OnNewLayer)

       # create the menu bar
       menuBar = Wx::MenuBar.new
       menuBar.append(fileMenu,    "&File")
       menuBar.append(actionsMenu, "Actions")
       menuBar.append(layersMenu,  "Layers")
       menuBar.append(viewMenu,    "View")
       menuBar.append(helpMenu,    "&Help")

       self.menu_bar = menuBar
    end

#   def create_infopanel
#       rect = self.get_rect()
#       @infoFrame = InfoFrame.new(self,
#                                    pos=(rect.x+rect.width+1, rect.y),
#                                    size=(200, rect.height))
#   end

    def notify_layer_change(notification)
        menuBar = get_menu_bar()
        layers = menuBar.get_menu(menuBar.find_menu("Layers"))
        item = layers.find_item(layers.find_item(notification.layer))
        if not item.is_checked()
            item.check()
        end
    end

    def OnQuit(event)
        self.destroy()
    end

    def OnAbout(event)
        dlg = Wx::MessageDialog.new(self, "Keyboard remapper for the TypeMatrix 2030\n© 2007 David Whetstone",
                                "About Remapper", Wx::OK | Wx::ICON_INFORMATION)
        dlg.show_modal()
        dlg.destroy()
    end

    def OnHelp(event)
        dlg = Wx::MessageDialog.new(self, "The gods help them that help themselves.\n--  Aesop",
                               "Remapper Help", Wx::OK | Wx::ICON_INFORMATION)
        dlg.show_modal()
        dlg.destroy()
    end

    def OnOpen(event)
        dlg = Wx::MessageDialog.new(self, "This would be an open Dialog\nIf there was anything to open\n",
                                "Open File", Wx::OK | Wx::ICON_INFORMATION)
        dlg.show_modal()
        dlg.destroy()
    end

    def OnPrefs(event)
        dlg = Wx::MessageDialog.new(self, "This would be an preferences Dialog\nIf there were any preferences to set.\n",
                                "Preferences", Wx::OK | Wx::ICON_INFORMATION)
        dlg.show_modal()
        dlg.destroy()
    end

    def OnNewLayer(event)
        dlg = Wx::MessageDialog.new(self, "Yay!  A new layer!",
                               "New Layer", Wx::OK | Wx::ICON_INFORMATION)
        dlg.show_modal()
        dlg.destroy()
    end

    def OnChangeLayer(event)
        item = self.GetMenuBar().FindItemById(event.GetId())
        layer = item.GetText()
        LayerChangeNotification(layer).notify()
    end

    def NotifyLayerChange(notification)
        menuBar = self.GetMenuBar()
        layers = menuBar.GetMenu(menuBar.FindMenu("Layers"))
        item = layers.FindItemById(layers.FindItem(notification.layer))
        if not item.IsChecked()
            item.Check()
        end
    end

    def OnNewKey(event)
        if @newKeyPane == nil
            @newKeyPane = NewKeyPane.new(@sp)
            evt_button(@newKeyPane.cancelButton) {|event| OnNewKeyCancel(event)}
            evt_button(@newKeyPane.okButton) {|event| OnNewKeyOK(event)}
#           self.Bind(Wx::EVT_BUTTON, self.OnNewKeyCancel, @newKeyPane.cancelButton)
#           self.Bind(Wx::EVT_BUTTON, self.OnNewKeyOK, @newKeyPane.okButton)
            @sp.replace_window(@destPane, @newKeyPane)
            @destPane.hide()
        else
            Wx::Bell()
        end
    end

    def OnNewKeyOK(event)
        @sp.replace_window(@newKeyPane, @destPane)
        @destPane.show()
        @newKeyPane.destroy()
        @newKeyPane = nil
    end

    def OnNewKeyCancel(event)
        print "hello"
        @sp.replace_window(@newKeyPane, @destPane)
        @destPane.show()
        @newKeyPane.destroy()
        @newKeyPane = nil
    end

    def OnEditKey(event)
        if @newKeyPane == nil
            keyHandle = getSelectedKeyHandle
            @newKeyPane = NewKeyPane.new(@sp, keyHandle)
            evt_button(@newKeyPane.okButton) {|event| OnNewKeyOK }
#           self.Bind(Wx::EVT_BUTTON, self.OnNewKeyOK, @newKeyPane.okButton)
            @sp.replace_window(@destPane, @newKeyPane)
            @destPane.hide()
        else
            Wx::bell()
        end
    end

    def getSelectedKeyHandle
        window = Wx::Window.find_focus
        return window.GetSelectedKeyHandle()
    end

#   def OnShowInfo(event)
#       if @infoFrame == nil
#           createInfopanel()
#       end
#       item = self.GetMenuBar().FindItemById(event.GetId())
#       if @infoFrame.IsShown()
#           @infoFrame.Hide()
#           item.SetText('Show Info\tCtrl+I')
#       else
#           @infoFrame.show()
#           item.SetText('Hide Info\tCtrl+I')
#       end
#   end

    def OnClick(event)
        kb = repr(Model.keyboard.org)
        self.button.SetLabel(kb)
    end
end

if $0 == __FILE__
    Wx::App.run do
        Model.StaticInit()
        frame = MainFrame.new.show
    end
end
