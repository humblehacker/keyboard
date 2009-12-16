#!/usr/bin/env ruby

require 'wx'

require 'model'
require 'frame'


class App < Wx::App

    def on_init
        Model.StaticInit()
        result = MainFrame.new.show()
        return result
    end
end

if $0 == __FILE__
    App.new.main_loop
end

