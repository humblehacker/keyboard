class Notification

    @@observers = {}

    def initialize(value)
        @value = value
    end

    def Notification.add_observer(callback)
        if not @@observers.has_key?(self.__id__)
            @@observers[self.__id__] = []
        end
        @@observers[self.__id__] << callback
    end

    def Notification.remove_observer(callback)
        @@observers.delete(callback)
    end

    def Notification.notify(value)
        if @@observers.has_key?(self.__id__)
            @@observers[self.__id__].each do |callback|
                callback.call(new(value))
            end
        end
    end
end

class KeyUpdateNotification < Notification
    def eid; @value; end
end

class LayerChangeNotification < Notification
    def layer; @value; end
end

class ModelChangeNotification < Notification
    def keyboardModel; @value; end
end

class CategoryChangeNotification < Notification
    def category; @value; end
end

if $0 == __FILE__

    class SomeOther < Notification
        def val; @value; end
    end

    class Test

        def initialize()
            KeyUpdateNotification.add_observer(self.method(:OnKeyUpdate))
            SomeOther.add_observer(self.method(:OnSomeOther))
        end

        def OnKeyUpdate(note)
            puts note.eid
        end

        def OnSomeOther(note)
            puts note.val
        end
    end

    test = Test.new()

    KeyUpdateNotification.notify(100)
    puts
    SomeOther.notify(200)

end



