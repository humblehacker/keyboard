import os
from os import path

import pprint
from pprint import pformat
import logging
from logging import debug
from re import match
from xml.sax import make_parser
from xml.sax.handler import ContentHandler
from copy import deepcopy

from hid import HIDUsageTable
from keyboard import KeyLayout, KeyMap, RowDef, KeyRef, \
                     KeyDef, MacroKey, Modifiers, Keyboard
from util import Point, Size
from notifications import ModelChangeNotification

basepath = path.join(os.getcwd(), 'xml')

def extractRev(rev):
    return match(r'\$Rev: ([0-9]+) \$', rev).group(1)

def processModifier(attrs):
    eid = attrs['id']
    if eid == 'Left Alt':
        return Modifiers['L_ALT']
    if eid == 'Left Ctrl':
        return Modifiers['L_CTRL']
    if eid == 'Left Shift':
        return Modifiers['L_SHFT']
    if eid == 'Left GUI':
        return Modifiers['L_GUI']
    if eid == 'Right Alt':
        return Modifiers['R_ALT']
    if eid == 'Right Ctrl':
        return Modifiers['R_CTRL']
    if eid == 'Right Shift':
        return Modifiers['R_SHFT']
    if eid == 'Right GUI':
        return Modifiers['R_GUI']
    raise RuntimeError, "Unknown modifier '%s'" % eid

class SourceKey(object):

    def __init__(self, handle):
        self.handle = handle
        self.usage  = None
        self.mode   = ''
        self.macro  = []
        self.labels = {}

    def __str__(self):
        return "handle: %s, labels: %s" % (self.handle, self.labels)

class Category(object):

    def __init__(self, name):
        self.name        = name
        self.keyHandles = []

    def __str__(self):
        return "Category: %s with keys: %s" % (self.name, self.keyHandles)

class SourceKeysCH(ContentHandler):

    def __init__(self, hid):
        ContentHandler.__init__(self)
        self.hid = hid
        self.state = ['Root']
        self.keys = {}
        self.content = None
        self.currentKey = None

    def processUsage(self, keyHandle, attrs):
        # Get the Usage Page
        # since usage names are unique across all pages, the usage page
        # specified is only used as a sanity check against the page
        # retrieved from the usage tables.
        usagePage = 'Keyboard and Keypad'
        if attrs.has_key('page'):
            usagePage = attrs['page']
        if not self.hid.usagePagesByName.has_key(usagePage):
            raise RuntimeError("SourceKeys: Key '%s' while looking up '%s'" % (keyHandle, usagePage))
        usagePage = self.hid.usagePagesByName[usagePage]

        # Get the Usage ID
        usageID = attrs['id']
        if not self.hid.usagesByName.has_key(usageID):
            raise RuntimeError("SourceKeys: Usage '%s' not found for key '%s'" % (usageID, keyHandle))
        usage = self.hid.usagesByName[usageID]
        if usage.page != usagePage: # sanity check
            raise RuntimeError("SourceKeys: Usage page mismatch '%s'\nShould be '%s', but '%s' was specified." % \
                                (usageID, usage.page, usagePage))
        return usage

    def startElement(self, name, attrs):
        last = self.state[-1]
        while True:
            if last == 'Root':
                if name == 'SourceKeys':
                    self.state.append(name)
                    break

            if last == 'SourceKeys':
                if name == 'Key':
                    self.state.append(name)
                    keyHandle = attrs['id']
                    self.currentKey = self.keys[keyHandle] = SourceKey(keyHandle)
                    break

            # <SourceKeys> sub-elements
            elif last == 'Key':
                if name == 'Label':
                    self.state.append('Label')
                    break
                if name == 'Usage':
                    self.currentKey.usage = self.processUsage(self.currentKey.handle, attrs)
                    break
                if name == 'MacroKey':
                    self.currentKey.macro.append(MacroKey())
                    self.state.append('MacroKey')
                    break
                if name == 'Macro':
                    self.state.append('Macro')
                    break
                if name =='ModeKey':
                    def anon(chars):
                        self.currentKey.mode += chars
                    self.content = anon
                    break

            # <Macro> sub-elements
            elif last == 'Macro':
                if name == 'MacroKey':
                    self.currentKey.macro.append(MacroKey())
                    self.state.append('MacroKey')
                    break
                if name == 'Usage':
                    self.currentKey.macro.append(self.processUsage(self.currentKey.handle, attrs))
                    break

            # <Key> sub-elements
            elif last == 'Label':
                if attrs.has_key('color'):
                    legendColor = self.kb.colors[attrs['color']]
                note = None
                if attrs.has_key('note'):
                    note = attrs['note']
                if name == 'TopLeft' or name == 'TopCenter' or name == 'TopRight' or \
                   name == 'BottomLeft' or name == 'BottomCenter' or name == 'BottomRight' or \
                   name == 'Center':
                    self.state.append(name)
                    def anon(chars):
                        self.currentKey.labels[name] = chars
                    self.content = anon
                    break
            elif last == 'MacroKey':
                if name == 'Modifier':
                    self.currentKey.macro[-1].modifiers |= processModifier(attrs)
                    break
                if name == 'Usage':
                    if self.currentKey.macro[-1].usage != None:
                        raise RuntimeError, "multiple usages specified for macro key at %s" % self.currentKey.location
                    self.currentKey.macro[-1].usage = self.processUsage(self.currentKey.handle, attrs)
                    break

            break

    def characters(self, chars):
        if self.content != None and match(r'\S', chars) != None:
            debug("chars = <%s>", chars)
            self.content(chars)

    def endElement(self, name):
        last = self.state[-1]
        while True:
            if last == 'SourceKeys':
                if name == last:
                    self.state.pop()
                    break

            elif last == 'Key':
                if name == last:
                    self.currentKey = None
                    self.state.pop()
                    break
                if name == 'Usage':
                    break
                if name == 'ModeKey':
                    self.content = None
                    break
            # <Key> sub-elements
            elif last == 'Label':
                if name == last:
                    self.state.pop()
                    break
            elif last == 'Macro':
                if name == last:
                    self.state.pop()
                    break
            elif last == 'MacroKey':
                if name == last:
                    self.state.pop()
                    break
                if name =='Usage' or name == 'Modifier':
                    break
            # <Label> sub-elements
            elif last == 'TopLeft' or last == 'TopCenter' or last == 'TopRight' or \
                 last == 'BottomLeft' or last == 'BottomCenter' or last == 'BottomRight' or \
                 last == 'Center' :
                if name == last:
                    self.content = None
                    self.state.pop()
                    break
            break

class CategoriesCH(ContentHandler):

    def __init__(self):
        ContentHandler.__init__(self)
        self.state = ['Root']
        self.categories = {}

    def startElement(self, name, attrs):
        last = self.state[-1]
        while True:
            if last == 'Root':
                if name == 'Categories':
                    self.state.append(name)
                    break

            if last == 'Categories':
                if name == 'Category':
                    self.state.append(name)
                    self.currentCategory = Category(attrs['name'])
                    self.categories[self.currentCategory.name] = self.currentCategory
                    break

            if last == 'Category':
                if name == 'KeyRef':
                    keyHandle = attrs['id']
                    self.currentCategory.keyHandles.append(keyHandle)
                    break
            break

    def endElement(self, name):
        last = self.state[-1]
        while True:
            if last == 'Categories':
                if name == 'Categories':
                    self.state.pop()
                    break

            if last == 'Category':
                if name == 'Category':
                    self.state.pop()
                    break
            break


class KbContentHandler(ContentHandler):

    def __init__(self, sourceModel):
        ContentHandler.__init__(self)
        self.sourceModel = sourceModel
        self.content = None
        self.copyright = ""
        self.level = 0

        self.state = ['Root']
        self.content = None
        self.kb = None
        self.currentKeyDef = None
        self.currentRowDef = None
        self.currentRow = 0
        self.pos = Point(0.0, 0.0)
        self.currentKeyMap = None
        self.currentKey = None
        self.currentColor = None
        self.defaultColor = None
        self.currentUsagePage = ''
        self.currentUsageID = ''
        self.currentMatrixRow = 0

    def include(self, filename):
        debug("Parsing file: %s", filename)
        parser = make_parser()
        parser.setContentHandler(self)
        parser.parse(path.join(basepath, filename))

    def startElement(self, name, attrs):
        # handle XIncludes
        if name == 'xi:include':
            self.include(attrs['href'])
            return

        self.level += 1
        debug("%s<%s %s>", ' '*self.level, name, pprint.saferepr(attrs.items()))

        last = self.state[-1]
        while True:
            # Root elements
            if last == 'Root':
                if name == 'Keyboard':
                    platform = None
                    if attrs.has_key('platform'):
                        platform = attrs['platform']
                    self.kb = Keyboard(attrs['org'], platform)
                    self.kb.copyright = self.copyright
                    self.state.append('Keyboard')
                    break
                if name == 'Copyright':
                    self.state.append('Copyright')
                    def anon(chars):
                        self.copyright += chars
                    self.content = anon
                    break

            # Root sub-elements
            elif last == 'Keyboard':
                if name == 'Layout':
                    eid = attrs['id']
                    rev = extractRev(attrs['rev'])
                    self.kb.layout = KeyLayout(eid, rev)
                    self.state.append('Layout')
                    break
                if name == 'Map':
                    eid = attrs['id']
                    rev = extractRev(attrs['rev'])
                    if not attrs.has_key('base'):
                        if not self.kb.platformMap == None:
                            self.kb.maps.append(deepcopy(self.kb.platformMap))
                            self.kb.maps[-1].ids.append(eid)
                            self.kb.maps[-1].revs.append(rev)
                        else:
                            self.kb.maps.append(KeyMap(eid, rev))
                    else:
                        self.include(attrs['base'])
                        self.kb.maps[-1].ids.append(eid)
                        self.kb.maps[-1].revs.append(rev)
                    self.currentKeyMap = self.kb.maps[-1]
                    self.state.append('Map')
                    break
                if name == 'Matrix':
                    self.kb.matrixId = attrs['id']
                    self.state.append('Matrix')
                    break

            # <Keyboard> sub-elements
            elif last == 'Layout':
                if name == 'Spacing':
                    def anon(chars):
                        self.kb.layout.spacing = float(chars)
                    self.content = anon
                    break
                if name == 'Colors':
                    self.kb.colors = {}
                    self.state.append('Colors')
                    break
                if name == 'Mount':
                    self.kb.layout.mount = Size(0.0, 0.0)
                    self.state.append('Mount')
                    break
                if name == 'KeyDefs':
                    self.state.append('KeyDefs')
                    break
            elif last == 'Map':
                if name == 'Keys':
                    if attrs.has_key('default_color'):
                        self.defaultColor = self.kb.colors[attrs['default_color']]
                    self.state.append('Keys')
                    break
            elif last == 'Matrix':
                if name == 'Row':
                    self.currentMatrixRow = int(attrs['id'])
                    self.kb.matrix.append({})
                    self.state.append('MatrixRow')
                    break

            # <Matrix> sub-elements
            elif last == 'MatrixRow':
                if name == 'Col':
                    matrixCol = int(attrs['id'])
                    def anon(chars):
                        self.kb.matrix[self.currentMatrixRow][matrixCol] = chars
                    self.content = anon
                    break

            # <Layout> sub-elements
            elif last == 'Colors':
                if name == 'Color':
                    self.state.append('Color')
                    self.currentColor = attrs['name']
                    break
            elif last == 'Mount':
                if name == 'Height':
                    def anon(chars):
                        self.kb.layout.mount.height = float(chars)
                        self.content = anon
                    break
                if last == 'Width':
                    def anon(chars):
                        self.kb.layout.mount.width = float(chars)
                    self.content = anon
                    break
            elif last == 'KeyDefs':
                if name == 'Row':
                    self.pos.x  = 0.0
                    self.currentRow += 1
                    self.currentRowDef = RowDef(self.currentRow)
                    self.state.append('KeyDefRow')
                    break

            # <KeyDefs> sub-elements
            elif last == 'KeyDefRow':
                if name == 'OffsetY':
                    def anon(chars):
                        self.currentRowDef.offset.y = float(chars)
                        self.pos.y += self.currentRowDef.offset.y + self.kb.layout.spacing
                    self.content = anon
                    break

                if name == 'OffsetX':
                    def anon(chars):
                        self.currentRowDef.offset.x = float(chars)
                        self.pos.x += self.currentRowDef.offset.x
                    self.content = anon
                    break
                if name == 'KeyDef':
                    location = attrs['location']
                    self.currentKeyDef = KeyDef(location)
                    self.kb.keyhash[location] = self.currentKeyDef
                    self.currentKeyDef.origin = deepcopy(self.pos)
                    self.state.append('KeyDef')
                    break

            # <Row> (of <KeyDef>) sub-elements
            elif last == 'KeyDef':
                if name == 'Height':
                    def anon(chars):
                        self.currentKeyDef.size.height = float(chars)
                    self.content = anon
                    break
                if name == 'Width':
                    def anon(chars):
                        self.currentKeyDef.size.width = float(chars)
                        self.pos.x += self.currentKeyDef.size.width + self.kb.layout.spacing
                    self.content = anon
                    break
                if name == 'OffsetY':
                    def anon(chars):
                        self.currentKeyDef.offset.y = float(chars)
                        self.currentKeyDef.origin.y = self.pos.y + self.currentKeyDef.offset.y
                    self.content = anon
                    break
                if name == 'OffsetX':
                    def anon(chars):
                        self.currentKeyDef.offset.x = float(chars)
                        self.currentKeyDef.origin.x = self.pos.x + self.currentKeyDef.offset.x
                    self.content = anon
                    break
                if name == 'Background' or name == 'Bump' or name == 'NullKey':
                    break

            # <Colors> sub-elements
            elif last == 'Color':
                if name == 'Rgb':
                    def anon(chars):
                        self.kb.colors[self.currentColor] = chars
                    self.content = anon
                    break

            # <Map> sub-elements
            elif last == 'Keys':
                if name == 'KeyRef':
                    location = attrs['location']
                    keyHandle = attrs['id']
                    if not self.kb.keyhash.has_key(location):
                        raise RuntimeError, "Keymap %s: %s: Key definition %s has not been defined" % (self.currentKeyMap, keyHandle, location)
                    if self.kb.keyhash[location].isNullKey:
                        raise RuntimeError, "Keymap %s: %s: Cannot assign key to a NullKey definition (%s)" % (self.currentKeyMap, keyHandle, location)
                    if not self.sourceModel.has_key(keyHandle):
                        raise RuntimeError("Keymap %s: Key with id '%s' for location '%s' does not exist in SourceKeys" % (self.currentKeyMap, keyHandle, location))
                    oldKey = None
                    if self.currentKeyMap.keys.has_key(location):
                        oldKey = self.currentKeyMap.keys[location]
                    self.currentKey = self.currentKeyMap.keys[location] = KeyRef(location, keyHandle)
                    self.currentKey.prevKey = oldKey
                    break

            else:
                raise RuntimeError("Unknown state '%s'" % last)
            raise RuntimeError("Unknown element '%s' for state '%s'" % (name, last))

    def characters(self, chars):
        if self.content != None and match(r'\S', chars) != None:
            debug("chars = <%s>", chars)
            self.content(chars)

    def endElement(self, name):
        # handle XIncludes
        if name == 'xi:include':
            return

        debug("%s</%s>", ' '*self.level, name)
        self.level -= 1

        last = self.state[-1]
        while True:
            if last == 'Root':
                pass
            elif last == 'Copyright':
                if name == last:
                    #TODO: clean up copyright -- self.copyright.strip!
                    self.state.pop()
                    content = None
                    break
            elif last == 'Keyboard':
                if name == last:
                    #TODO: remove platform keymap
                    self.state.pop()
                    break

            # <Keyboard> sub-elements
            elif last == 'Layout':
                if name == last:
                    self.state.pop()
                    # Maybe load the platform map
                    if self.kb.platform != None:
                        self.include("Map-%s.xml" % self.kb.platform)
                        self.kb.maps[-1].platform = True
                        self.kb.platformMap = self.kb.maps[-1]
                    break
                if name == 'Spacing':
                    self.content = None
                    break
                if name == 'KeyDefs': #or name == 'xi:include':
                    break
            elif last == 'Map':
                if name == last:
                    self.currentKeyMap = None
                    self.state.pop()
                    break
            elif last == 'Matrix':
                if name == last:
                    self.state.pop()
                    break

            # <Matrix> sub-elements
            elif last == 'MatrixRow':
                if name == 'Row':
                    self.state.pop()
                    break
                if name == 'Col':
                    self.content = None
                    break

            # <Layout> sub-elements
            elif last == 'Colors':
                if name == last:
                    self.state.pop()
                    break
            elif last == 'Mount':
                if name == last:
                    self.state.pop()
                    break
                if name == 'Height' or name == 'Width':
                    content = None
                    break
            elif last == 'KeyDefs':
                if name == last:
                    self.state.pop()
                    break

            # <KeyDefs> sub-elements
            elif last == 'KeyDefRow':
                if name == 'Row':
                    while len(self.kb.layout.rows) <= self.currentRow:
                        self.kb.layout.rows.append(None)
                    self.kb.layout.rows[self.currentRow] = self.currentRowDef
                    self.currentRowDef = None
                    self.state.pop()
                    break
                if name == 'OffsetX' or name == 'OffsetY':
                    self.content = None
                    break

            # <Row> (of <KeyDef>) sub-elements
            elif last =='KeyDef':
                if name == last:
                    self.kb.maxSize.width  = max(self.kb.maxSize.width,  self.currentKeyDef.origin.x + self.currentKeyDef.size.width)
                    self.kb.maxSize.height = max(self.kb.maxSize.height, self.currentKeyDef.origin.y + self.currentKeyDef.size.height)
                    self.currentRowDef.keydefs.append(self.currentKeyDef)
                    self.currentKeyDef = None
                    self.state.pop()
                    break
                if name == 'Height' or name == 'Width' or name == 'OffsetX' or name == 'OffsetY' or name == 'Background':
                    self.content = None
                    break
                if name == 'NullKey':
                    self.currentKeyDef.isNullKey = True
                    break
                if name == 'Bump':
                    break

            # <Colors> sub-elements
            elif last == 'Color':
                if name == last:
                    self.currentColor = None
                    self.state.pop()
                    break
                if name == 'Rgb':
                    self.content = None
                    break

            # <Map> sub-elements
            elif last == 'Keys':
                if name == last:
                    self.state.pop()
                    break
                if name =='KeyRef':
                    self.currentKey = None
                    break

            else:
                raise RuntimeError("Unknown state '%s'" % last)
            raise RuntimeError("Unknown element '%s' for state '%s'" % (name, last))

class KeyboardModel(object):

    def __init__(self, sourceModel):
        parser = make_parser()
        handler = KbContentHandler(sourceModel)
        parser.setContentHandler(handler)
        fname = path.join(basepath, '2030-B.xml')
        parser.parse(fname)
        self.kb = handler.kb
        ModelChangeNotification(self).notify()

class SourceModel(object):

    def __init__(self):
        fname = path.join(basepath, 'HIDUsageTables.xml')
        self.hid = HIDUsageTable(fname)
        parser = make_parser()
        handler = SourceKeysCH(self.hid)
        parser.setContentHandler(handler)
        fname = path.join(basepath, 'SourceKeys.xml')
        parser.parse(fname)
        self.keys = handler.keys

class CategoriesModel(object):

    def __init__(self):
        parser = make_parser()
        handler = CategoriesCH()
        parser.setContentHandler(handler)
        fname = path.join(basepath, 'Categories.xml')
        parser.parse(fname)
        self.categories = handler.categories

class Model(object):

    sourcekeys = None
    keyboard   = None
    categories = None

    @staticmethod
    def StaticInit():
        Model.sourcekeys = SourceModel().keys
        Model.keyboard   = KeyboardModel(Model.sourcekeys).kb
        Model.categories = CategoriesModel().categories

def main():

    Model.StaticInit()

    print "\nSourceKeys"
    for key in Model.sourcekeys:
        print Model.sourcekeys[key]

    print "\nCategories"
    print type(Model.categories)
    for category in Model.categories.values():
        print category

    print "\nKeyboard"
    print Model.keyboard.org
#   print "keymaps: %s" % [str(keymap) for keymap in keyboardModel.kb.maps]
    for keymap in Model.keyboard.maps:
        print "Keymap %s" % keymap.ids[-1]
        for key in keymap.keys.values():
            print key

if __name__ == '__main__':
    main()

