import xcb
import xcb.xproto
import xcb.randr

RRScreenChangeNotifyMask = 1 << 0 # from randr.h

def main():
    conn = xcb.connect()
    conn.randr = conn(xcb.randr.key)

    setup = conn.get_setup()
    root = setup.roots[0].root

    print "XRRSelectInput"
    conn.randr.SelectInput(root, RRScreenChangeNotifyMask) # as seen in http://www.mail-archive.com/sawfish-list@gnome.org/msg03630.html

    conn.flush()

    while True:
        e = conn.wait_for_event()
        print e, vars(e)

if __name__ == "__main__":
    main()
