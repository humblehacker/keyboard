class Notification(object):

    @classmethod
    def AddObserver(cls, observerFunc):
        cls._observers.append(observerFunc)

    @classmethod
    def RemoveObserver(cls, observerFunc):
        cls._observers.remove(observerFunc)

    def notify(self):
        for updateFunc in self.__class__._observers:
            updateFunc(self)

class KeyUpdateNotification(Notification):

    _observers = []
    def __init__(self, eid):
        self.eid = eid

class LayerChangeNotification(Notification):

    _observers = []
    def __init__(self, layer):
        self.layer = layer

class ModelChangeNotification(Notification):

    _observers = []
    def __init__(self, keyboardModel):
        self.keyboardModel = keyboardModel

class CategoryChangeNotification(Notification):

    _observers = []
    def __init__(self, category):
        self.category = category

def main():

    class Test:
        def __init__(self):
            KeyUpdateNotification.AddObserver(self.OnKeyUpdate)
            SomeOther.AddObserver(self.OnSomeOther)

        def OnKeyUpdate(self, note):
            print note.eid

        def OnSomeOther(self, note):
            print note.val

    class SomeOther(Notification):

        _observers = []
        def __init__(self, val):
            Notification.__init__(self)
            self.val = val

    test = Test()

    notification = KeyUpdateNotification(100)
    notification.notify()
    print
    notification = SomeOther(200)
    notification.notify()

if __name__ == '__main__':
    main()




