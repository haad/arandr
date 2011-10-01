# ARandR -- Another XRandR GUI
# Copyright (C) 2008 -- 2011 chrysn <chrysn@fsfe.org>
# 
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# 
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

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
