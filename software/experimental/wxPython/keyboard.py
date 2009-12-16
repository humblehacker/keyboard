from util import Point, Size

Modifiers     = { "L_CTRL":(1<<0), "L_SHFT":(1<<1), "L_ALT":(1<<2), "L_GUI":(1<<3), \
                  "R_CTRL":(1<<4), "R_SHFT":(1<<5), "R_ALT":(1<<6), "R_GUI":(1<<7) }
ModifierCodes = { "L_CTRL":'LC',   "L_SHFT":'LS',   "L_ALT":'LA',   "L_GUI":'LG', \
                  "R_CTRL":'RC',   "R_SHFT":'RS',   "R_ALT":'RA',   "R_GUI":'RG' }

class Keyboard(object):

  def __init__(self, org, platform):
      self.org = org
      self.platform = platform
      self.keyhash = {}
      self.copyright = ''
      self.maxSize = Size(0,0)
      self.matrix = []
      self.maps   = []
      self.platformMap = None
      self.layout = None

class KeyLayout(object):

    def __init__(self, eid, rev):
        self.eid    = eid
        self.rev    = rev
        self.rows   = []

class KeyDef(object):

    def __init__(self, location):
        self.location  = location
        self.origin    = Point(0.0, 0.0)
        self.size      = Size(0.0, 0.0)
        self.isNullKey = False
        self.offset    = Point(0.0, 0.0)

class RowDef(object):
    def __init__(self, row):
        self.row     = row
        self.offset  = Point(0.0, 0.0)
        self.keydefs = []

class KeyMap(object):

    def __init__(self, eid, rev):
        self.ids  = [eid]
        self.revs = [rev]
        self.keys = {}

    def __str__(self):
        if (self.ids[0] == None):
            return ""
        return self.ids[-1]

class KeyRef(object):
    """Connnect a KeyDef location to a SourceKey handle."""

    def __init__(self, location, keyHandle):
        self.location  = location
        self.keyHandle = keyHandle

    def __str__(self):
        return "location: %s keyHandle: %s" % (self.location, self.keyHandle)

class MacroKey(object):

    def __init__(self):
        self.usage     = None
        self.modifiers = 0

    def MakeHandle(self, index):
        return "macro:%d:%s:%s:%d" % (index, self.usage.page.name, self.usage.name, self.modifiers)



