require 'rubygems'
#require 'wx'

require 'hid'
require 'keyboard'
require 'notifications'

if $basepath == nil
    $basepath = Dir.getwd
end
$xmlpath = File.join($basepath, 'xml')

def extractRev(rev)
    return /\$Rev: ([0-9]+) \$/.match(rev)[1]
end

def processModifier(attrs)
    eid = attrs['id']
    return Modifiers['L_ALT']  if eid == 'Left Alt'
    return Modifiers['L_CTRL'] if eid == 'Left Ctrl'
    return Modifiers['L_SHFT'] if eid == 'Left Shift'
    return Modifiers['L_GUI']  if eid == 'Left GUI'
    return Modifiers['R_ALT']  if eid == 'Right Alt'
    return Modifiers['R_CTRL'] if eid == 'Right Ctrl'
    return Modifiers['R_SHFT'] if eid == 'Right Shift'
    return Modifiers['R_GUI']  if eid == 'Right GUI'
    raise "Unknown modifier '#{eid}'"
end

class SourceKey

    attr_accessor :handle, :usage, :mode, :macro, :labels

    def initialize(handle)
        @handle = handle
        @usage  = nil
        @mode   = ''
        @macro  = []
        @labels = {}
    end

    def to_s
        return "handle: #{@handle}, labels: #{@labels}"
    end
end

class Category

    attr_accessor :name, :keyHandles

    def initialize(name)
        @name       = name
        @keyHandles = []
    end

    def to_s
        return "Category: #{@name} with keys: #{@keyHandles}"
    end
end

class SourceKeysCH
    extend XML::SaxParser::Callbacks

    attr_reader :keys

    def initialize(hid)
        @hid = hid
        @state = [:Root]
        @keys = {}
        @content = nil
        @currentKey = nil
    end

    def processUsage(keyHandle, attrs)
        # Get the Usage Page
        # since usage names are unique across all pages, the usage page
        # specified is only used as a sanity check against the page
        # retrieved from the usage tables.
        usagePage = 'Keyboard and Keypad'
        if attrs.has_key?('page')
            usagePage = attrs['page']
        end
        if not @hid.usagePagesByName.has_key?(usagePage)
            raise "SourceKeys: Key '#{keyHandle}' while looking up '#{usagePage}'"
        end
        usagePage = @hid.usagePagesByName[usagePage]

        # Get the Usage ID
        usageID = attrs['id']
        if not @hid.usagesByName.has_key?(usageID)
            raise "SourceKeys: Usage '#{usageID}' not found for key '#{keyHandle}'"
        end
        usage = @hid.usagesByName[usageID]
        if usage.page != usagePage # sanity check
            raise "SourceKeys: Usage page mismatch '#{usageID}'\nShould be '#{usage.page}', but '#{usagePage}' was specified."
        end
        return usage
    end

    def dumpstate
        result = "{ "
        @state.each {|st| result += "[#{st}] "}
        result += "}"
        return result
    end

    def on_start_document()
    end

    def on_end_document()
    end

    def on_start_element(name, attrs)
#       puts
#       puts "+#{dumpstate()}"
#       puts "++ #{name}"
        case @state.last
        when :Root
            case name
            when 'SourceKeys'
                @state.push :SourceKeys
            end

        when :SourceKeys
            case name
            when 'Key'
                @state.push :Key
                keyHandle = attrs['id']
                @currentKey = @keys[keyHandle] = SourceKey.new(keyHandle)
            end

        # <SourceKeys> sub-elements
        when :Key
            case name
            when 'Label'
                @state.push :Label
            when 'Usage'
                @currentKey.usage = processUsage(@currentKey.handle, attrs)
            when 'MacroKey'
                @currentKey.macro.push MacroKey.new()
                @state.push :MacroKey
            when 'Macro'
                @state.push :Macro
            end
            if name =='ModeKey':
                @content = lambda {|chars| @currentKey.mode += chars }
            end

        # <Macro> sub-elements
        when :Macro
            case name
            when 'MacroKey'
                @currentKey.macro.push MacroKey.new()
                @state.push :MacroKey
            when 'Usage'
                @currentKey.macro.push processUsage(@currentKey.handle, attrs)
            end

        # <Key> sub-elements
        when :Label
            if attrs.has_key?('color'):
                legendColor = @kb.colors[attrs['color']]
            end
            note = nil
            if attrs.has_key?('note'):
                note = attrs['note']
            end
            case name
            when 'TopLeft', 'TopCenter', 'TopRight', 'BottomLeft', 'BottomCenter', 'BottomRight', 'Center'
                @state.push :"#{name}"
                @content = lambda {|chars| @currentKey.labels[name] = chars}
            end
        when :MacroKey
            case name
            when 'Modifier'
                @currentKey.macro.last.modifiers |= processModifier(attrs)
            when 'Usage'
                if @currentKey.macro.last.usage != nil:
                    raise "multiple usages specified for macro key at #{@currentKey.location}"
                end
                @currentKey.macro.last.usage = self.processUsage(@currentKey.handle, attrs)
            end
        else
#           raise "ERROR: Unknown element #{name} for state #{state}"
            raise "ERROR: Unknown state #{state}"
        end
    end

    def on_characters(chars)
        if @content != nil
#           puts "#{@content} .#{chars}."
            @content.call(chars)
        end
    end

    def on_end_element(name)
        case @state.last
        when :Root
        when :SourceKeys
            case name
            when 'SourceKeys'
                @state.pop
            end
        when :Key
            case name
            when 'Key'
                @currentKey = nil
                @state.pop
            when 'Usage'
            when 'ModeKey'
                @content = nil
            end
        # <Key> sub-elements
        when :Label
            case name
            when 'Label'
                @state.pop
            end
        when :Macro
            case name
            when 'Macro'
                @state.pop
            end
        when :MacroKey
            case name
            when 'MacroKey'
                @state.pop
            end
            if name =='Usage' or name == 'Modifier':
            end
        # <Label> sub-elements
        when :TopLeft, :TopCenter, :TopRight, :BottomLeft, :BottomCenter, :BottomRight, :Center
            case name
            when 'TopLeft', 'TopCenter', 'TopRight', 'BottomLeft', 'BottomCenter', 'BottomRight', 'Center'
                @content = nil
                @state.pop
            end
        else
            raise "ERROR: Unknown state #{@state}"
        end
#       puts "-- #{name}"
#       puts "-#{dumpstate()}}"

    end

    def on_processing_instruction(target, data)
    end

    def on_comment(msg)
    end

end

class Category

    def initialize(name)
        @name       = name
        @keyHandles = []
    end

    def to_str
        return "Category: #{@name} with keys: #{@keyHandles}"
    end
end

class CategoriesCH
    extend XML::SaxParser::Callbacks

    attr_reader :categories

    def initialize
        @state = [:Root]
        @categories = {}
    end

    def on_start_document()
    end

    def on_end_document()
    end

    def on_start_element(name, attrs)
#       puts
#       puts "+#{dumpstate()}"
#       puts "++ #{name}"

        case @state.last
        when :Root
            if name == 'Categories'
                @state.push :"#{name}"
            end
        when :Categories
            if name == 'Category'
                @state.push :"#{name}"
                @currentCategory = Category.new(attrs['name'])
                @categories[@currentCategory.name] = @currentCategory
            end
        when :Category
            if name == 'KeyRef'
                keyHandle = attrs['id']
                @currentCategory.keyHandles.push keyHandle
            end
        end
    end

    def on_characters(chars)
    end

    def on_end_element(name)
        last = @state.last
        case last
        when :Categories
            if name == 'Categories':
                @state.pop
            end
        when :Category
            if name == 'Category':
                @state.pop
            end
        end
#       puts "-- #{name}"
#       puts "-#{dumpstate()}}"
    end

    def on_processing_instruction(target, data)
    end

    def on_comment(msg)
    end

    def dumpstate
        result = "{ "
        @state.each {|st| result += "[#{st}] "}
        result += "}"
        return result
    end

end

class CategoriesModel

    attr_reader :categories

    def initialize
        handler = CategoriesCH.new()
        parser = XML::SaxParser.new
        parser.callbacks = handler
        parser.filename = File.join($xmlpath, 'Categories.xml')
        parser.parse
        @categories = handler.categories
    end
end

class SourceModel #< Wx::Object
    attr_reader :keys
    def initialize
        fname   = File.join($xmlpath, 'HIDUsageTables.xml')
        @hid    = HIDUsageTable.new(fname)

        handler = SourceKeysCH.new(@hid)
        parser = XML::SaxParser.new
        parser.callbacks = handler
        parser.filename = File.join($xmlpath, 'SourceKeys.xml')
        parser.parse
        @keys  = handler.keys
#       puts @keys
    end
end

class KeyboardCH
    extend XML::SaxParser::Callbacks

    attr_reader :kb

    def initialize(sourceModel)
        @sourceModel = sourceModel
        @content = nil
        @copyright = ""
        @level = 0

        @state = [:Root]
        @content = nil
        @kb = nil
        @currentKeyDef = nil
        @currentRowDef = nil
        @currentRow = 0
        @pos = Point.new(0.0, 0.0)
        @currentKeyMap = nil
        @currentKey = nil
        @currentColor = nil
        @defaultColor = nil
        @currentUsagePage = ''
        @currentUsageID = ''
        @currentMatrixRow = 0
    end

    def include(filename)
#       debug("Parsing file: %s", filename)
        parser = XML::SaxParser.new
        parser.callbacks = self
        parser.filename = File.join($xmlpath, filename)
        parser.parse
    end

    def on_start_document()
    end

    def on_end_document()
    end

    def on_start_element(name, attrs)
        # handle XIncludes
        if name == 'xi:include':
            include(attrs['href'])
            return
        end

        @level += 2
#       puts
#       puts "+#{' '*@level}#{dumpstate()}"
#       puts "+#{' '*@level}<#{name} #{attrs}>"

        case @state.last
        # Root elements
        when :Root
            case name
            when 'Keyboard'
                platform = nil
                if attrs.has_key?('platform'):
                    platform = attrs['platform']
                end
                @kb = Keyboard.new(attrs['org'], platform)
                @kb.copyright = @copyright
                @state.push :Keyboard
            when 'Copyright'
                @state.push :Copyright
                @content = lambda {|chars| @copyright += chars }
            end

        # Root sub-elements
        when :Keyboard
            case name
            when 'Layout'
                eid = attrs['id']
                rev = extractRev(attrs['rev'])
                @kb.layout = KeyLayout.new(eid, rev)
                @state.push :Layout
            when 'Map'
                eid = attrs['id']
                rev = extractRev(attrs['rev'])
                if not attrs.has_key?('base')
                    if not @kb.platformMap == nil
                        @kb.maps.push(deepcopy(@kb.platformMap))
                        @kb.maps.last.ids.push(eid)
                        @kb.maps.last.revs.push(rev)
                    else
                        @kb.maps.push(KeyMap.new(eid, rev))
                    end
                else
                    include(attrs['base'])
                    @kb.maps.last.ids.push(eid)
                    @kb.maps.last.revs.push(rev)
                end
                @currentKeyMap = @kb.maps.last
                @state.push :Map
            when 'Matrix'
                @kb.matrixId = attrs['id']
                @state.push :Matrix
            end

        # <Keyboard> sub-elements
        when :Layout
            case name
            when 'Spacing'
                @content = lambda {|chars| @kb.layout.spacing = chars.to_f}
            when 'Colors'
                @kb.colors = {}
                @state.push :Colors
            when 'Mount'
                @kb.layout.mount = Size.new(0.0, 0.0)
                @state.push :Mount
            when 'KeyDefs'
                @state.push :KeyDefs
            end
        when :Map
            case name
            when 'Keys'
                if attrs.has_key?('default_color'):
                    @defaultColor = @kb.colors[attrs['default_color']]
                end
                @state.push :Keys
            end
        when :Matrix
            case name
            when 'Row'
                @currentMatrixRow = attrs['id'].to_i
                @kb.matrix.push({})
                @state.push :MatrixRow
            end

        # <Matrix> sub-elements
        when :MatrixRow
            case name
            when 'Col'
                matrixCol = attrs['id'].to_i
                @content = lambda{|chars| @kb.matrix[@currentMatrixRow][matrixCol] = chars}
            end

        # <Layout> sub-elements
        when :Colors
            case name
            when 'Color'
                @state.push :Color
                @currentColor = attrs['name']
            end
        when :Mount
            case name
            when 'Height'
                @content = lambda {|chars| @kb.layout.mount.height = chars.to_f}
            when 'Width'
                @content = lambda {|chars| @kb.layout.mount.width = chars.to_f}
            end
        when :KeyDefs
            case name
            when 'Row'
                @pos.x  = 0.0
                @currentRow += 1
                @currentRowDef = RowDef.new(@currentRow)
                @state.push :KeyDefRow
            end

        # <KeyDefs> sub-elements
        when :KeyDefRow
            case name
            when 'OffsetY'
                @content = lambda {|chars| @currentRowDef.offset.y = chars.to_f;
                                           @pos.y += @currentRowDef.offset.y + @kb.layout.spacing}

            when 'OffsetX'
                @content = lambda {|chars| @currentRowDef.offset.x = chars.to_f;
                                           @pos.x += @currentRowDef.offset.x}
            when 'KeyDef'
                location = attrs['location']
                @currentKeyDef = KeyDef.new(location)
                @kb.keyhash[location] = @currentKeyDef
                @currentKeyDef.origin = @pos.dup
                @state.push :KeyDef
            end

        # <Row> (of <KeyDef>) sub-elements
        when :KeyDef
            case name
            when 'Height'
                @content = lambda {|chars| @currentKeyDef.size.height = chars.to_f}
            when 'Width'
                @content = lambda {|chars| @currentKeyDef.size.width = chars.to_f;
                    @pos.x += @currentKeyDef.size.width + @kb.layout.spacing}
            when 'OffsetY'
                @content = lambda {|chars| @currentKeyDef.offset.y = chars.to_f;
                    @currentKeyDef.origin.y = @pos.y + @currentKeyDef.offset.y}
            when 'OffsetX'
                @content = lambda {|chars| @currentKeyDef.offset.x = chars.to_f;
                    @currentKeyDef.origin.x = @pos.x + @currentKeyDef.offset.x}
            when 'Background', 'Bump', 'NullKey'
            end

        # <Colors> sub-elements
        when :Color
            case name
            when 'Rgb'
                @content = lambda {|chars| @kb.colors[@currentColor] = chars}
            end

        # <Map> sub-elements
        when :Keys
            case name
            when 'KeyRef'
                location = attrs['location']
                keyHandle = attrs['id']
                if not @kb.keyhash.has_key?(location):
                    raise "Keymap #{@currentKeyMap}: #{keyHandle}: Key definition #{location} has not been defined"
                end
                if @kb.keyhash[location].isNullKey:
                    raise "Keymap #{@currentKeyMap}: #{keyHandle}: Cannot assign key to a NullKey definition (#{location})"
                end
                if not @sourceModel.has_key?(keyHandle):
                    raise "Keymap #{@currentKeyMap}: Key with id '#{keyHandle}' for location '#{location}' does not exist in SourceKeys"
                end
                oldKey = nil
                if @currentKeyMap.keys.has_key?(location):
                    oldKey = @currentKeyMap.keys[location]
                end
                @currentKey = @currentKeyMap.keys[location] = KeyRef.new(location, keyHandle)
                @currentKey.prevKey = oldKey
            end
        else
            raise "Unknown state '#{@state.last}'"
        end

#       raise "Unknown element '#{name}' for state '#{@state.last}'"
    end

    def on_characters(chars)
        if @content != nil
#           puts "#{@content} .#{chars}."
            @content.call(chars)
        end
    end

    def on_end_element(name)
        # handle XIncludes
        if name == 'xi:include':
            return
        end

#       debug("%s</%s>", ' '*@level, name)
        @level -= 2

        case @state.last
        when :Root
            pass
        when :Copyright
            case name
            when 'Copyright'
                #TODO: clean up copyright -- @copyright.strip!
                @state.pop()
                content = nil
            end
        when :Keyboard
            case name
            when 'Keyboard'
                #TODO: remove platform keymap
                @state.pop()
            end

        # <Keyboard> sub-elements
        when :Layout
            case name
            when 'Layout'
                @state.pop()
                # Maybe load the platform map
                if @kb.platform != nil:
                    include("Map-%s.xml" % @kb.platform)
                    @kb.maps.last.platform = True
                    @kb.platformMap = @kb.maps.last
                end
            when 'Spacing'
                @content = nil
            when 'KeyDefs' #or name == 'xi:include':
            end
        when :Map
            case name
            when 'Map'
                @currentKeyMap = nil
                @state.pop()
            end
        when :Matrix
            case name
            when 'Matrix'
                @state.pop()
            end

        # <Matrix> sub-elements
        when :MatrixRow
            case name
            when 'Row'
                @state.pop()
            when 'Col'
                @content = nil
            end

        # <Layout> sub-elements
        when :Colors
            case name
            when 'Colors'
                @state.pop()
            end
        when :Mount
            case name
            when 'Mount'
                @state.pop()
            when 'Height', 'Width'
                content = nil
            end
        when :KeyDefs
            case name
            when 'KeyDefs'
                @state.pop()
            end

        # <KeyDefs> sub-elements
        when :KeyDefRow
            case name
            when 'Row'
                while @kb.layout.rows.length <= @currentRow:
                    @kb.layout.rows.push(nil)
                end
                @kb.layout.rows[@currentRow] = @currentRowDef
                @currentRowDef = nil
                @state.pop()
            when 'OffsetX', 'OffsetY'
                @content = nil
            end

        # <Row> (of <KeyDef>) sub-elements
        when :KeyDef
            case name
            when 'KeyDef'
                @kb.maxSize.width  = [@kb.maxSize.width,  @currentKeyDef.origin.x + @currentKeyDef.size.width].max
                @kb.maxSize.height = [@kb.maxSize.height, @currentKeyDef.origin.y + @currentKeyDef.size.height].max
                @currentRowDef.keydefs.push(@currentKeyDef)
                @currentKeyDef = nil
                @state.pop()
            when 'Height', 'Width', 'OffsetX', 'OffsetY', 'Background'
                @content = nil
            when 'NullKey'
                @currentKeyDef.isNullKey = true
            when 'Bump'
            end

        # <Colors> sub-elements
        when :Color
            case name
            when 'Color'
                @currentColor = nil
                @state.pop()
            when 'Rgb'
                @content = nil
            end

        # <Map> sub-elements
        when :Keys
            case name
            when 'Keys'
                @state.pop()
            when 'KeyRef'
                @currentKey = nil
            end
        else
            raise "Unknown state '#{@state.last}'"
        end

#       puts "-#{' '*@level}#{name}"
#       puts "-#{' '*@level}#{dumpstate()}"

#        raise "Unknown element '#{name}' for state '#{@state.last}'"
    end

    def on_processing_instruction(target, data)
    end

    def on_comment(msg)
    end

    def dumpstate
        result = "{ "
        @state.each {|st| result += "[#{st}] "}
        result += "}"
        return result
    end

end

class KeyboardModel

    attr_reader :kb

    def initialize(sourceModel)
        handler = KeyboardCH.new(sourceModel)
        parser = XML::SaxParser.new
        parser.callbacks = handler
        parser.filename = File.join($xmlpath, '2030-B.xml')
        parser.parse
        @kb = handler.kb
        ModelChangeNotification.notify(self)
    end
end

class Model #< Wx::Object
    @@sourcekeys = nil
    def self.StaticInit()
        @@sourcekeys = SourceModel.new.keys
        @@categories = CategoriesModel.new.categories
        @@keyboard   = KeyboardModel.new(Model.sourcekeys).kb
    end

    def self.sourcekeys
        @@sourcekeys
    end

    def self.categories
        @@categories
    end

    def self.keyboard
        @@keyboard
    end
end

def main()

    Model.StaticInit()

    puts "\nSourceKeys"
    Model.sourcekeys.each do |key, value|
        puts "#{key} => #{value}"
    end

    puts "\nCategories"
    puts Model.categories.class
    Model.categories.each do |key, value|
        puts "#{key} => #{value}"
    end

    puts "\nKeyboard"
    puts Model.keyboard.org
#   puts "keymaps: %s" % [str(keymap) for keymap in keyboardModel.kb.maps]
    Model.keyboard.maps.each do |keymap|
        puts "#keymap #{keymap.ids.last}"
        keymap.keys.each do |key, value|
            puts "#{key} => #{value}"
        end
    end
end

if $0 == __FILE__
    main
end

