"""Demo application, primarily used to make sure the screenlayout library can be used independent of ARandR.

Run by calling the main() function."""

import gtk
from . import widget

def main():
    w = gtk.Window()
    w.connect('destroy',gtk.main_quit)

    r = widget.ARandRWidget()
    r.load_from_x()

    b = gtk.Button("Reload")
    b.connect('clicked', lambda *args: r.load_from_x())

    b2 = gtk.Button("Apply")
    b2.connect('clicked', lambda *args: r.save_to_x())

    v = gtk.VBox()
    w.add(v)
    v.add(r)
    v.add(b)
    v.add(b2)
    w.set_title('Simple ARandR Widget Demo')
    w.show_all()
    gtk.main()
