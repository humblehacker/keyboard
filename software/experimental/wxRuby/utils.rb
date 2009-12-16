#!/usr/bin/env ruby
#
#  Created by David Whetstone on 2007-03-28.
#  Copyright (c) 2007. All rights reserved.


class Point
  attr_accessor :x, :y
  def initialize(x, y)
    @x = x
    @y = y
  end

  def offset(point)
    @x += point.x
    @y += point.y
    return self
  end

  def + (point)
    return Point.new(point.x + @x, point.y + @y)
  end

  def to_s
    "(#{@x}, #{@y})"
  end

  def to_a
    [@x, @y]
  end
end

class Size
  attr_accessor :width, :height
  def initialize(w, h)
    @width = w
    @height = h
  end

  def *(rhs)
      return Size.new(@width * rhs, @height * rhs)
  end

  def to_s
    "(#{@width}, #{@height})"
  end

  def to_a
    [@width, @height]
  end
end

def max?(a, b)
  a > b ? a : b
end

class Rect

    attr_reader :size, :origin

    def initialize(x, y, width, height)
      @origin = Point.new(x,y)
      @size   = Size.new(width, height)
    end

    def self.new_with_rect(rect)
#       return Rect.new(rect.x.to_f, rect.y.to_f,
#                       rect.width.to_f, rect.height.to_f)
        return Rect.new(rect.x, rect.y, rect.width, rect.height)
    end

    def self.new_with_nsrect(rect)
        return Rect.new(rect.origin.x, rect.origin.y, rect.size.width, rect.size.height)
    end
    def x=(x)
      @origin.x = x
    end

    def y=(y)
      @origin.y = y
    end

    def width=(width)
      @size.width = width
    end

    def height=(height)
      @size.height = height
    end

    def x
      return @origin.x
    end

    def y
      return @origin.y
    end

    def width
      return @size.width
    end

    def height
      return @size.height
    end

    def top
      return @origin.y
    end

    def left
      return @origin.x
    end

    def bottom
      return @origin.y + @size.height - 1
    end

    def right
      return @origin.x + @size.width - 1
    end

    def OffsetXY(x, y)
      @origin.x += x
      @origin.y += y
      return self
    end

    def Offset(point)
      OffsetXY(point.x, point.y)
      return self
    end

    def Inflate(width, height)
      @origin.x -= width / 2
      @size.width += width
      @origin.y -= height / 2
      @size.height += height
      return self
    end

    def Deflate(width, height)
      return Inflate(-width, -height)
    end

    def Contains(point)
      return ((point.x >= @origin.x and point.x <= (@origin.x + @size.width)) and
              (point.y >= @origin.y and point.y <= (@origin.y + @size.height)))
    end

    def CenterIn(rect)
      return Rect.new(rect.x + (rect.width - @size.width)/2,
                      rect.y + (rect.height - @size.height)/2,
                      @size.width, @size.height)
    end

    def * (scale)
      return Rect.new(@origin.x * scale, @origin.y * scale,
                      @size.width * scale, @size.height * scale)
    end

#   def *= (scale)
#     @origin *= scale
#     @size *= scale
#     return self
#   end

    def / (scale)
      return Rect(@origin.x / scale, @origin.y / scale,
                  @size.width / scale, @size.height / scale)
    end

#   def /= (scale)
#     @origin /= scale
#     @size /= scale
#     return self
#   end

    def to_s
      return "(#{@origin.x} #{@origin.y} #{@size.width} #{@size.height})"
    end

    def Get
      return [@origin.x, @origin.y, @size.width, @size.height]
    end

    def to_wxRect
        return Wx::Rect.new(@origin.x.to_i, @origin.y.to_i,
                            @size.width.to_i, @size.height.to_i)
    end

    def __getitem__(index)
      return Get()[index]
    end

    def __setitem__(index, val)
      if index == 0; @x = val
      elsif index == 1; @y = val
      elsif index == 2; @width = val
      elsif index == 3; @height = val
      else  raise IndexError
      end
    end
end

class Includes
  def initialize
    @includes = []
  end

  def push(path)
    @includes.push path.strip
  end

  def find_file(filename)
    newname = nil
    @includes.each do |inc|
      newname = "#{inc}/#{filename}"
      return newname if File.exist?(newname)
    end
    return nil
  end
end

def normalize_number( number )
  return number.to_i(16) if number =~ /^0x/
  return number.to_i
end

def normalize_identifier(identifier)
  normalized = identifier.upcase
  normalized.gsub!(/_/,  '_UNDERSCORE')
  normalized.gsub!(/!/,  '_EXCLAMATION')
  normalized.gsub!(/\?/, '_QUESTION')
  normalized.gsub!(/@/,  '_AT')
  normalized.gsub!(/#/,  '_POUND')
  normalized.gsub!(/\$/, '_DOLLAR')
  normalized.gsub!(/%/,  '_PERCENT')
  normalized.gsub!(/\^/, '_CARET')
  normalized.gsub!(/&/,  '_AMPERSAND')
  normalized.gsub!(/\*/, '_ASTERISK')
  normalized.gsub!(/\./, '_PERIOD')
  normalized.gsub!(/\,/, '_COMMA')
  normalized.gsub!(/;/,  '_SEMICOLON')
  normalized.gsub!(/:/,  '_COLON')
  normalized.gsub!(/=/,  '_EQUALS')
  normalized.gsub!(/\+/, '_PLUS')
  normalized.gsub!(/\-/, '_MINUS')
  normalized.gsub!(/\(/, '_LPAREN')
  normalized.gsub!(/\)/, '_RPAREN')
  normalized.gsub!(/\[/, '_LSQUAREBRACKET')
  normalized.gsub!(/\]/, '_RSQUAREBRACKET')
  normalized.gsub!(/\{/, '_LCURLYBRACE')
  normalized.gsub!(/\}/, '_RCURLYBRACE')
  normalized.gsub!(/>/,  '_GREATERTHAN')
  normalized.gsub!(/</,  '_LESSTHAN')
  normalized.gsub!(/\\/, '_BACKSLASH')
  normalized.gsub!(/\//, '_SLASH')
  normalized.gsub!(/\~/, '_TILDE')
  normalized.gsub!(/\|/, '_PIPE')
  normalized.gsub!(/'/,  '_APOSTROPHE')
  normalized.gsub!(/"/,  '_QUOTE')
  normalized.gsub!(' ',  '_')
  return normalized
end

def normalize_filename(filename)
  normalized = filename.gsub(/-/, '_')
  return normalized
end

def unknown_element_error(element, state)
  error = "Parse error: Unknown element '#{element}' for [ "
  state.each {|x| error << ':' << x.to_s << ' ' }
  error << ']'
  return error
end

def unknown_modifier_error(modifier)
  error = "Parse error: Unknown modifier '#{modifier}'"
  return error
end
