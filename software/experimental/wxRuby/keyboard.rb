require 'utils.rb'

Modifiers     = { "L_CTRL" => (1<<0), "L_SHFT" => (1<<1), "L_ALT" => (1<<2), "L_GUI" => (1<<3), \
                  "R_CTRL" => (1<<4), "R_SHFT" => (1<<5), "R_ALT" => (1<<6), "R_GUI" => (1<<7) }
ModifierCodes = { "L_CTRL" => 'LC',   "L_SHFT" => 'LS',   "L_ALT" => 'LA',   "L_GUI" => 'LG', \
                  "R_CTRL" => 'RC',   "R_SHFT" => 'RS',   "R_ALT" => 'RA',   "R_GUI" => 'RG' }

class Keyboard

    attr_accessor :copyright, :layout, :colors, :keyhash, :maxSize, :platform, :matrixId,
                  :matrix, :platformMap, :maps, :org

    def initialize(org, platform)
        @org = org
        @platform = platform
        @keyhash = {}
        @copyright = ''
        @maxSize = Size.new(0,0)
        @matrix = []
        @maps   = []
        @platformMap = nil
        @layout = nil
        @colors = {}

        @matrixId = 0
    end
end

class KeyLayout

    attr_accessor :spacing, :eid, :ref, :rows

    def initialize(eid, rev)
        @eid    = eid
        @rev    = rev
        @rows   = []
        @spacing = nil
    end
end

class KeyDef

    attr_accessor :location, :origin, :size, :isNullKey, :offset

    def initialize(location)
        @location  = location
        @origin    = Point.new(0.0, 0.0)
        @size      = Size.new(0.0, 0.0)
        @isNullKey = false
        @offset    = Point.new(0.0, 0.0)
    end
end

class RowDef

    attr_accessor :keydefs, :row, :offset

    def initialize(row)
        @row     = row
        @offset  = Point.new(0.0, 0.0)
        @keydefs = []
    end
end

class KeyMap

    attr_accessor :keys, :revs, :ids

    def initialize(eid, rev)
        @ids  = [eid]
        @revs = [rev]
        @keys = {}
    end

    def to_s
        if (@ids[0] == nil)
            return ""
        end
        return @ids.last
    end
end

class KeyRef
    # Connnect a KeyDef location to a SourceKey handle.

    attr_accessor :prevKey, :keyHandle

    def initialize(location, keyHandle)
        @location  = location
        @keyHandle = keyHandle

        @prevKey = nil
    end

    def to_s
        return "location: #{@location} keyHandle: #{@keyHandle}"
    end
end

class MacroKey
    attr_accessor :modifiers, :usage

    def initialize
        @usage     = nil
        @modifiers = 0
    end

    def MakeHandle(index)
        return "macro:#{index}:#{@usage.page.name}:#{@usage.name}:#{@modifiers}"
    end
end



