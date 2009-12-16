# -*- coding: iso-8859-1 -*-
#
#  DestDisplayKey.rb
#  Keys.rb
#
#  Created by David Whetstone on 6/27/08.
#  Copyright (c) 2008 RedGoat Software, Inc. All rights reserved.
#

require 'osx/cocoa'
include OSX

require 'DisplayKey'

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
