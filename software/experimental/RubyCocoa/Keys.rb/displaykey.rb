#
#  displaykey.rb
#  Keys
#
#  Created by David on 6/19/08.
#  Copyright (c) 2008 __MyCompanyName__. All rights reserved.
#

require 'utils'
require 'model'
require 'notifications'

class DisplayKey

    attr_reader :handle, :unscaled
    attr_accessor :scaled, :labelRect

     def initialize(handle, unscaled)
         # A DisplayKey handle may be, but is not necessarily, a SourceKey handle
         @handle = handle
         @unscaled = unscaled
         @scaled = nil
         # this wasn't here in the Python version, how did it work?
         @labelRect = nil
     end

     def handle
         return display_handle
     end

     def display_handle
         return @handle
     end

     def source_handle
         return @handle
     end

     def to_s
         return "{#{@handle}: unscaled: #{@unscaled} scaled: #{@scaled}}"
     end
end
