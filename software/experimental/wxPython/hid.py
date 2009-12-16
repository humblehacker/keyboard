from xml.sax import make_parser
from xml.sax.handler import ContentHandler

class UsagePage:
    """docstring for UsagePage"""
    def __init__(self):
        self.name = ''
        self.id = ''
        self.usages = []

class Usage:
    """docstring for Usage"""
    def __init__(self, page):
        self.page = page
        self.name = ''
        self.id = ''

    def MakeHandle(self, index=None):
        if index is not None:
            return "m_usage:%d:%s:%s" % (index, self.page.name, self.name)
        else:
            return "usage:%s:%s" % (self.page.name, self.name)


class HIDUsageTable:
    """docstring for HIDUsageTable"""
    def __init__(self, filename):
        self.filename = filename
        self.usagePagesByName = {}
        self.usagesByName = {}
        self.usagePages = []
        parser = make_parser()
        handler = HIDContentHandler(self)
        parser.setContentHandler(handler)
        parser.parse(filename)


class HIDContentHandler(ContentHandler):
    """docstring for HIDContentHandler"""
    def __init__(self, hid):
        ContentHandler.__init__(self)
        self._hid = hid
        self._state = ['Root']
        self._currentUsagePage = None
        self._currentUsage = None
        self._content = None

    def _updateUsagePageName(self, chars):
        self._currentUsagePage.name += chars
        # print "Page: %s" % self._currentUsagePage.name

    def _updateUsagePageId(self, chars):
        self._currentUsagePage.id = chars
        # print "Page: %s" % self._currentUsagePage.id

    def _updateUsageName(self, chars):
        self._currentUsage.name += chars
        # print "Usage: %s" % self._currentUsage.name

    def _updateUsageId(self, chars):
        self._currentUsage.id = chars
        # print "Usage: %s" % self._currentUsage.id

    def _addUsage(self, usage, page):
        """docstring for _addUsage"""
        # print "adding usage '%s' to page '%s'\n" % (usage.name, page.name)
        if self._hid.usagesByName.has_key(usage.name):
            prev = self._hid.usagesByName[usage.name]
            raise RuntimeError(
                 "Duplicate name: '%s' for id '%s' and page '%s'\nPrevious: id '%s' page '%s'"
                 % (usage.name, usage.id, page.name, prev.id, prev.page.name))
        self._hid.usagesByName[usage.name] = usage
        page.usages.append(usage)

    def startElement(self, name, attrs):
        # print
        # print "+" + str(self._state)
        # print "++ %s" % name

        last = self._state[-1]
        while True:
            if last == 'Root':
                if name == 'HID':
                    self._state.append('HID')
                    break
            elif last == 'HID':
                if name == 'UsagePages':
                    self._state.append('UsagePages')
                    break
            elif last == 'UsagePages':
                if name == 'UsagePage':
                    self._state.append('UsagePage')
                    self._currentUsagePage = UsagePage()
                    break
            elif last == 'UsagePage':
                if name == 'Name':
                    self._content = self._updateUsagePageName
                    break
                elif name == 'ID':
                    self._content = self._updateUsagePageId
                    break
                elif name == 'UsageIDs':
                    self._state.append('UsageIDs')
                    break
            elif last == 'UsageIDs':
                if name == 'UsageID':
                    self._state.append('UsageID')
                    self._currentUsage = Usage(self._currentUsagePage)
                    break
            elif last == 'UsageID':
                if name == 'Name':
                    self._content = self._updateUsageName
                    break
                elif name == 'ID':
                    self._content = self._updateUsageId
                    break
                elif name == 'UsageType' or name == 'Section':
                    break
            else:
                raise RuntimeError("Unknown state %s" % last)
            raise RuntimeError("Unknown element %s for state %s" % (name, last))


    def characters(self, chars):
        if self._content != None:
            self._content(chars)

    def endElement(self, name):
        """docstring for endElement"""
        last = self._state[-1]
        while True:
            if last == 'Root':
                break
            elif last == 'HID':
                if name == 'HID':
                    self._state.pop()
                    break
            elif last == 'UsagePages':
                if name == 'UsagePages':
                    self._state.pop()
                    self._currentUsagePage = None
                    break
            elif last == 'UsagePage':
                if name == 'UsagePage':
                    if self._hid.usagePagesByName.has_key(self._currentUsagePage.name):
                        raise RuntimeError("Duplicate page name: %s for %s" \
                                           % (self._currentUsagePage.name, self._currentUsagePage.id))
                    self._hid.usagePagesByName[self._currentUsagePage.name] = self._currentUsagePage
                    self._hid.usagePages.append(self._currentUsagePage)
                    self._currentUsagePage = None
                    self._state.pop()
                    break
                if name == 'Name' or name == 'ID':
                    self._content = None
                    break
            elif last == 'UsageIDs':
                if name == 'UsageIDs':
                    self._state.pop()
                    break
            elif last == 'UsageID':
                if name == 'UsageID':
                    self._addUsage(self._currentUsage, self._currentUsagePage)
                    self._content = None
                    self._state.pop()
                    break
                if name == 'Name' or name == 'ID':
                    self._content = None
                    break
                if name == 'UsageType' or name == 'Section':
                    break
            else:
                raise RuntimeError("Unknown state %s" % last)
            raise RuntimeError("Unknown element %s for state %s" % (name, last))

        # print "-- %s" % name
        # print "-" + str(self._state)


if __name__ == "__main__":
    from os import path
    hid = HIDUsageTable(path.join('.', 'xml', 'HIDUsageTables.xml'))
    for page in hid.usagePages:
        print page.name
