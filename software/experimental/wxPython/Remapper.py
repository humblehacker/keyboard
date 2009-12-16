import wx
import logging
from logging import error, debug
import traceback
from frame import MainFrame
from model import Model

# Although my preference is to follow 'The Python Style Guide'
# [http://www.python.org/doc/essays/styleguide.html], wxPython does not.
# Rather than uglify my code with competing styles, I opt to follow
# wxPython's code guidelines [http://www.wxpython.org/codeguidelines.php],
# with the following exceptions:
#
# * Methods private to a class will be prefixed by a single underscore,
#   and be written in leadingLowerMixedCase.
# * Attribute and variable naming convention was not specified, they will
#   be written in leadingLowerMixedCase, with private attributes prefixed
#   by a single underscore

class App(wx.App):

    def OnInit(self):
        logging.basicConfig( \
            # level = logging.DEBUG \
            filename = "remapper.log" \
            )

        Model.StaticInit()
        frame = MainFrame()
        frame.Show()

        return True

def main():
    try:
        app = App()
        app.MainLoop()
    except:
        error("Unhandled exception")
        file = open("stacktrace", "w")
        traceback.print_exc(None, file)

if __name__ == '__main__':
    main()
