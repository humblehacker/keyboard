import wx

class Point(object):

    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __mul__(self, rhs):
        return Point(self.x * rhs, self.y * rhs)

    def __imul__(self, rhs):
        self.x *= rhs
        self.y *= rhs
        return self

    def __div__(self, rhs):
        return Point(self.x / rhs, self.y / rhs)

    def __idiv__(self, rhs):
        self.x /= rhs
        self.y /= rhs
        return self

    def __str__(self):
        return "(%s %s)" % (self.x, self.y)

    def Get(self):
        return (self.x, self.y)

    def __getitem__(self, index):
        return self.Get()[index]

    def __setitem__(self, index, val):
        if index == 0: self.x = val
        elif index == 1: self.y = val
        else: raise IndexError

class Size(object):

    def __init__(self, width, height):
        self.width = width
        self.height = height

    def __mul__(self, rhs):
        return Size(self.width * rhs, self.height * rhs)

    def __imul__(self, rhs):
        self.width  *= rhs
        self.height *= rhs
        return self

    def __div__(self, rhs):
        return Size(self.width / rhs, self.height / rhs)

    def __idiv__(self, rhs):
        self.width  /= rhs
        self.height /= rhs
        return self

    def __str__(self):
        return "(%s %s)" % (self.width, self.height)

    def Get(self):
        return (self.width, self.height)

    def __getitem__(self, index):
        return self.Get()[index]

    def __setitem__(self, index, val):
        if index == 0: self.width = val
        elif index == 1: self.height = val
        else: raise IndexError

class Rect(object):

    def __init__(self, x, y, width, height):
        self.origin = Point(x,y)
        self.size   = Size(width, height)

    def setX(self, x):
        self.origin.x = x

    def setY(self, y):
        self.origin.y = y

    def setWidth(self, width):
        self.size.width = width

    def setHeight(self, height):
        self.size.height = height

    def getX(self):
        return self.origin.x

    def getY(self):
        return self.origin.y

    def getWidth(self):
        return self.size.width

    def getHeight(self):
        return self.size.height

    def GetTop(self):
        return self.origin.y

    def GetLeft(self):
        return self.origin.x

    def GetBottom(self):
        return self.origin.y + self.size.height - 1

    def GetRight(self):
        return self.origin.x + self.size.width - 1

    def OffsetXY(self, x, y):
        self.origin.x += x
        self.origin.y += y
        return self

    def Offset(self, point):
        self.OffsetXY(point.x, point.y)
        return self

    def Inflate(self, width, height):
        self.origin.x -= width / 2
        self.size.width += width
        self.origin.y -= height / 2
        self.size.height += height
        return self

    def Deflate(self, width, height):
        return self.Inflate(-width, -height)

    def Contains(self, point):
        return (point.x >= self.origin.x and point.x <= (self.origin.x + self.size.width)) \
           and (point.y >= self.origin.y and point.y <= (self.origin.y + self.size.height))

    def CenterIn(self, rect):
        return Rect(rect.x + (rect.width - self.size.width)/2,
                    rect.y + (rect.height - self.size.height)/2,
                    self.size.width, self.size.height)

    def __mul__(self, scale):
        return Rect(self.origin.x * scale, self.origin.y * scale,
                    self.size.width * scale, self.size.height * scale)

    def __imul__(self, scale):
        self.origin *= scale
        self.size *= scale
        return self

    def __div__(self, scale):
        return Rect(self.origin.x / scale, self.origin.y / scale,
                    self.size.width / scale, self.size.height / scale)

    def __idiv__(self, scale):
        self.origin /= scale
        self.size /= scale
        return self

    def __str__(self):
        return "(%s %s %s %s)" % (self.x, self.y, self.width, self.height)

    def Get(self):
        return (self.origin.x, self.origin.y, self.size.width, self.size.height)

    def __getitem__(self, index):
        return self.Get()[index]

    def __setitem__(self, index, val):
        if index == 0: self.x = val
        elif index == 1: self.y = val
        elif index == 2: self.width = val
        elif index == 3: self.height = val
        else: raise IndexError

    x      = property(getX, setX)
    y      = property(getY, setY)
    width  = property(getWidth, setWidth)
    height = property(getHeight, setHeight)

def say(parent, message):
    dlg = wx.MessageDialog(parent, message, "Message", wx.OK | wx.CANCEL | wx.ICON_INFORMATION)
    dlg.ShowModal()
    dlg.Destroy()



