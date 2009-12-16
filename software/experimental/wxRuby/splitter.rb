require 'rubygems'
require 'wx'
#require 'wx.gizmos'

class MacSplitterWindow < Wx::SplitterWindow
    #   Subclass of the standard Wx::SplitterWindow to provide a more modern
    #   Mac-like splitter sash

    def initialize(parent, style)
        # style is ignored
        puts "here"
        super(parent, -1, Wx::DEFAULT_POSITION, Wx::DEFAULT_SIZE,
              Wx::SP_LIVE_UPDATE|Wx::SP_3DSASH)
         self.background_colour = Wx::Colour.new('#A5A5A5')
         evt_paint(:OnPaint)
         evt_splitter_sash_pos_changed(self.id,  :OnSashPosChanged)
         evt_splitter_sash_pos_changing(self.id, :OnSashPosChanging)
    end

    def OnPaint(event)
        paint do |dc|
            DrawSash(dc)
        end
        event.skip()
    end

    def OnSashPosChanged(event)
        event.skip()
    end

    def OnSashPosChanging(event)
        event.skip()
    end

    def DrawSash(dc)
        pos    = self.sash_position
        height = self.sash_size

        if self.split_mode == 1 #Wx::SPLIT_HORIZONTAL
            rect = Wx::Rect.new(0, pos+1, dc.size.width, height-2)
            dc.gradient_fill_linear(rect, Wx::Colour.new('#FCFCFC'), Wx::Colour.new('#DFDFDF'), Wx::SOUTH)
        end
    end

    def split_horizontally(window1, window2, sash_pos)
#       SetSashSize(10)
        super(window1, window2, sash_pos)
    end

    def split_vertically(window1, window2, sash_pos)
        self.sash_size = 1
        super(window1, window2, sash_pos)
    end

    def init_buffer()
        w, h = get_client_size()
        @buffer = Wx::EmptyBitmap.new(w, h)
        dc = Wx::BufferedDC.new(Wx::ClientDC.new(self), @buffer)
        DrawSash(dc)
    end
end

if RUBY_PLATFORM =~ /darwin/
    $SplitterWindow = MacSplitterWindow
else
    $SplitterWindow = Wx::SplitterWindow
end

if $0 == __FILE__
    Wx::App.run do
        hframe = Wx::Frame.new(nil, :title  => "source",
                                    :pos    => [200, 200],
                                    :size   => [400, 400])
        hsp = $SplitterWindow.new(hframe, :style => Wx::SP_LIVE_UPDATE | Wx::SP_3D)
        puts hsp.class
        left  = Wx::Panel.new(hsp)
        right = Wx::Panel.new(hsp)
        left.background_colour  = Wx::WHITE
        right.background_colour = Wx::WHITE
        left.hide()
        hsp.init(right)
        hsp.minimum_pane_size = 10
        hsp.split_horizontally(left, right, 100)
        hframe.show

        vframe = Wx::Frame.new(nil, :title  => "dest",
                                    :pos    => [650, 200],
                                    :size   => [400, 400])
        vsp = $SplitterWindow.new(vframe, :style => Wx::SP_LIVE_UPDATE | Wx::SP_3D)
        left  = Wx::Panel.new(vsp)
        right = Wx::Panel.new(vsp)
        left.background_colour  = Wx::WHITE
        right.background_colour = Wx::LIGHT_GREY
        left.hide()
        vsp.init(right)
        vsp.minimum_pane_size = 10
        vsp.split_vertically(left, right, 100)
        vframe.show
    end

end


