require 'xml/libxml'


class UsagePage
  attr_accessor :name, :id, :usages
  def initialize
    @name = ''
    @id = ''
    @usages = []
  end
end

class Usage
  attr_accessor :page, :id, :name
  def initialize(usagePage)
    @page = usagePage
    @id   = ''
    @name = ''
  end
  def MakeHandle(index=nil)
      if index != nil
          return "usage:#{index}:#{page.name}:#{name}"
      else
          return "usage:#{page.name}:#{name}"
      end
  end
end

class HIDUsageTable
    attr_reader :usagePages, :usages, :usagePagesByName, :usagesByName
    def initialize(filename)
        puts filename
        @filename         = filename
        @usagePagesByName = {}
        @usagesByName     = {}
        @usagePages       = []
        parser = XML::SaxParser.new
        parser.filename = filename
        parser.callbacks = HIDContentHandler.new(self)
        parser.parse
    end
end

class HIDContentHandler 
    extend XML::SaxParser::Callbacks

    def initialize(hid)
        @hid                = hid
        @state              = [:Root]
        @currentUsagePage   = nil
        @currentUsage       = nil
        @content            = nil  
    end

    def add_usage(usage, page)
#       puts "adding usage '#{usage.name}' to page '#{page.name}'\n"
        if @hid.usagesByName.has_key?(usage.name):
            prev = @hid.usagesByName[usage.name]
            raise "Duplicate name: '#{usage.name}' for id '#{usage.id}' and page '#{page.name}'\n"\
                  "Previous: id '#{prev.id}' page '#{prev.page.name}'"
        end
        @hid.usagesByName[usage.name] = usage
        page.usages.push usage
    end

    def on_start_document()
    end

    def on_end_document()
    end

    def dumpstate
        result = "{ "
        @state.each {|st| result += "[#{st}] "}
        result += "}"
        return result
    end

    def on_start_element(name, attr_hash)
#       puts
#       puts "+#{dumpstate()}"
#       puts "++ #{name}"
        case @state.last
        when :Root
            case name
            when "HID"
                @state.push :HID
            end
        when :HID
            case name
            when "UsagePages"
                @state.push :UsagePages
            end
        when :UsagePages
            case name
            when "UsagePage"
                @state.push :UsagePage
                @currentUsagePage = UsagePage.new
            end
        when :UsagePage
            case name
            when "Name"
                @content = lambda {|chars| @currentUsagePage.name += chars}   
            when "ID"
                @content = lambda {|chars| @currentUsagePage.id = chars}   
            when "UsageIDs"
                @state.push :UsageIDs
            end
        when :UsageIDs
            case name
            when "UsageID"
                @state.push :UsageID
                @currentUsage = Usage.new(@currentUsagePage)
            end
        when :UsageID
            case name
            when "Name"
                @content = lambda {|chars| @currentUsage.name += chars}   
            when "ID"
                @content = lambda {|chars| @currentUsage.id = chars}   
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
        when :HID
            case name
            when "HID"
                @state.pop
            end
        when :UsagePages
            case name
            when "UsagePages"
                @state.pop
                @currentUsagePage = nil
            end
        when :UsagePage
            case name
            when "UsagePage"
                if @hid.usagePagesByName.has_key?(@currentUsagePage.name)
                    raise "Duplicate page name: #{@currentUsagePage.name} for #{@currentUsagePage.id}"
                end
                @hid.usagePagesByName[@currentUsagePage.name] = @currentUsagePage
                @hid.usagePages.push @currentUsagePage
                @currentUsagePage = nil
                @state.pop
            when "Name", "ID"
                @content = nil 
            end
        when :UsageIDs
            case name
            when "UsageIDs"
                @state.pop
            end
        when :UsageID
            case name
            when "UsageID"
                add_usage(@currentUsage, @currentUsagePage)
                @content = nil
                @state.pop
            when "Name", "ID"
                @content = nil 
            when "UsageType", "Section"
                1
            end
        else
            raise "ERROR: Unknown state #{state}"
        end
#       puts "-- #{name}"
#       puts "-#{dumpstate()}}"

    end

    def on_processing_instruction(target, data)
    end


end

