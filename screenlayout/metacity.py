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

import os
import gobject
import gtk

try:
    import gconf
except ImportError:
    gconf = None

import gettext
gettext.install('arandr')

SCRIPTSDIR = os.path.expanduser('~/.screenlayout/') # must end in /

# cycling template:
# sh -c 'COUNT=`cat /tmp/counter 2>/dev/null`; LENGTH=3; COUNT=$(expr $(expr $COUNT + 1) % $LENGTH); echo $COUNT > /tmp/counter; case "$COUNT" in 0) echo zero;; 1) echo uno;; 2) echo dos;; esac'
# countfile must be a harmless string
CYCLINGPATTERN = """sh -c 'COUNTFILE=%(countfile)s; COUNT=`cat $COUNTFILE 2>/dev/null`; LENGTH=%(length)d; COUNT=$(expr $(expr $COUNT + 1) %% $LENGTH); echo $COUNT > $COUNTFILE; case "$COUNT" in %(cases)s;; esac'"""
CYCLINGPATTERN_RECOGNITION = [
        """sh -c 'COUNTFILE=""",
        """; COUNT=`cat $COUNTFILE 2>/dev/null`; LENGTH=""",
        """; COUNT=$(expr $(expr $COUNT + 1) % $LENGTH); echo $COUNT > $COUNTFILE; case "$COUNT" in """,
        """;; esac'""",
        ]

class MetacityWidget(gtk.Table):
    """Widget that manages bindings of screenlayout scripts to metacity keybindings.

    Not related to ARandR except that ARandR scripts are bound."""
    def __init__(self):
        gtk.Table.__init__(self, rows=13, columns=2)

        c = gconf.client_get_default()
        c.add_dir('/apps/metacity/global_keybindings', gconf.CLIENT_PRELOAD_NONE)
        c.add_dir('/apps/metacity/keybinding_commands', gconf.CLIENT_PRELOAD_NONE)

        self.attach(gtk.Label(_("Accelerator")), 0,1,0,1)
        self.attach(gtk.Label(_("Action")), 1,2,0,1)

        self.lines = []
        for i in range(1,13):
            k = KeyBindingButton(c, '/apps/metacity/global_keybindings/run_command_%d'%i)
            a = ActionWidget(c, '/apps/metacity/keybinding_commands/command_%d'%i)
            self.attach(k, 0, 1, i, i+1)
            self.attach(a, 1, 2, i, i+1)
            self.lines.append((k,a))
            k.connect('notify::bound', lambda *args: self._update())
            a.connect('notify::editable', lambda *args: self._update())
        self._update()

    def _update(self):
        for i,(k,a) in enumerate(self.lines):
            enable = (i==0 or k.props.bound or self.lines[i-1][0].props.bound) and a.props.editable
            k.props.sensitive = enable
            a.props.sensitive = enable and k.props.bound


class GConfButton(gtk.Button):
    """Button connected to a gconfkey via a gconf client c.

    Will call self._update when the key is changed; use self.set(value) to change the key's value."""
    def __init__(self, c, gconfkey):
        self._properties = {}
        super(GConfButton, self).__init__()

        self.gconf = c
        self.gconfkey = gconfkey
        self._id = c.notify_add(gconfkey, self._update)
        c.notify(gconfkey)

    def __del__(self):
        self.gconf.notify_remove(self._id)
        #print "del" # FIXME: not called!

    def do_get_property(self, key):
        return self._properties[key]
    def do_set_property(self, key, value):
        self._properties[key] = value

    def set(self, value):
        self.gconf.set_string(self.gconfkey, value)

    def _update(self, *args):
        """Called when the value of the key is changed (hooked into GConf); overwrite this."""
        pass


class KeyBindingButton(GConfButton):
    """GConfButton that will interpret the value as a keybinding and ask for a new keybinding when pressed."""
    __gproperties__ = {
            'bound': (gobject.TYPE_BOOLEAN, 'bound', 'slot is bound to a key', False, gobject.PARAM_READWRITE),
            }

    def __init__(self, *args, **kwords):
        super(KeyBindingButton, self).__init__(*args, **kwords)

        self.connect('clicked', self.on_clicked)
        self.connect('key-press-event', self.on_keypress)

    def _update(self, *args):
        s = self.gconf.get_string(self.gconfkey)

        if s == "disabled":
            self.props.label = _("disabled")
            self.props.bound = False
        else:
            self.props.label = s
            self.props.bound = True

        self.editing = False

    def abort_editing(self):
        self.editing = False
        self._update()

    def on_clicked(self, widget):
        if not self.editing:
            self.editing = True
            self.props.label = _("New accelerator...")
        else:
            self.abort_editing()

    def on_keypress(self, widget, event): # modified from gnome deskbar-applet's DeskbarPreferencesUI.py
        if not self.editing:
            return

        keymap = gtk.gdk.keymap_get_default()
        translation = keymap.translate_keyboard_state(event.hardware_keycode, event.state, event.group)
        if translation == None: # FIXME: metacity can also handle raw keycodes with modifiers (but can compiz?)
            accel_name = "%#x"%event.hardware_keycode
        else:
            (keyval, egroup, level, consumed_modifiers) = translation
            upper = event.keyval
            accel_keyval = gtk.gdk.keyval_to_lower(upper)

            # Put shift back if it changed the case of the key, not otherwise.
            if upper != accel_keyval and (consumed_modifiers & gtk.gdk.SHIFT_MASK):
                consumed_modifiers &= ~(gtk.gdk.SHIFT_MASK)

            # filter consumed/ignored modifiers
            ignored_modifiers = gtk.gdk.MOD2_MASK | gtk.gdk.MOD5_MASK
            accel_mods = event.state & gtk.gdk.MODIFIER_MASK & ~(consumed_modifiers | ignored_modifiers)

            if accel_mods == 0 and accel_keyval == gtk.keysyms.Escape:
                self.abort_editing()
                return
            if accel_mods == 0 and accel_keyval == gtk.keysyms.BackSpace:
                self.set('disabled')
                return

            if not gtk.accelerator_valid(accel_keyval, accel_mods):
                return # just modifiers

            accel_name = gtk.accelerator_name(accel_keyval, accel_mods)
            #self.set_accelerator(accel_keyval, event.hardware_keycode, accel_mods)
            #self.__old_value = None
            #self.emit('accel-edited', accel_name, accel_keyval, accel_mods, event.hardware_keycode)

        self.set(accel_name)

class ActionWidget(GConfButton):
    """GConfButton that will interpret the value as a command and allow changing it if it is a screenlayout script or a collection thereof."""
    __gproperties__ = {
            'editable': (gobject.TYPE_BOOLEAN, 'editable', 'true if property can be managed by MetacityWidget', False, gobject.PARAM_READWRITE),
            }

    def __init__(self, *args, **kwords):
        super(ActionWidget, self).__init__(*args, **kwords)

        self.connect('clicked', self.on_clicked)

    def _update(self, *args):
        s = self.gconf.get_string(self.gconfkey)

        if not s:
            self.props.label = _("no action")
            self.props.editable = True
            self.items = []
        elif s.startswith('"'+SCRIPTSDIR) and s.endswith('.sh"'):
            text = s[len(SCRIPTSDIR)+1:-4]

            self.props.label = text
            self.props.editable = True
            self.items = [text]
        elif s.startswith(CYCLINGPATTERN_RECOGNITION[0]):
            try:
                left = s[len(CYCLINGPATTERN_RECOGNITION[0]):]
                index = left.index(CYCLINGPATTERN_RECOGNITION[1])
                # countfile = left[:index] # not needed because not configurable. differing count files will be reset to the global one on change.
                left = left[index+len(CYCLINGPATTERN_RECOGNITION[1]):]
                index = left.index(CYCLINGPATTERN_RECOGNITION[2])
                length = int(left[:index])
                left = left[index+len(CYCLINGPATTERN_RECOGNITION[2]):]
                index = left.index(CYCLINGPATTERN_RECOGNITION[3])
                cases = left[:index]
                left = left[index+len(CYCLINGPATTERN_RECOGNITION[3]):]
                if left!="":
                    raise ValueError("Not my syntax.")

                # countfile, length, cases
                counter, scripts = zip(*[part.split(") ") for part in cases.split(" ;; ")])
                if counter != tuple(str(i) for i in range(length)):
                    raise ValueError("Not my syntax.")

                self.items = []
                for s in scripts:
                    if s.startswith('"'+SCRIPTSDIR) and s.endswith('.sh"'):
                        self.items.append(s[len(SCRIPTSDIR)+1:-4])
                    else:
                        raise ValueError("Not my syntax.");
            except (ValueError, ):
                self.props.label = _("incompatible configuration")
                self.props.editable = False
                self.items = None
                raise
            self.props.label = ", ".join(self.items)
            self.props.editable = True
        else:
            self.props.label = _("other application")
            self.props.editable = False
            self.items = None

    def on_clicked(self, widget):
        m = gtk.Menu()
        try:
            for f in os.listdir(SCRIPTSDIR):
                if not f.endswith('.sh'):
                    continue
                text = f[:-3]
                i = gtk.CheckMenuItem(text)
                if text in self.items:
                    i.props.active = True
                i.connect('activate', lambda menuitem, script: self.toggle(script), text)
                m.add(i)
        except OSError: # no such directory
            pass

        if not m.get_children():
            i = gtk.MenuItem(_("No files in %(folder)r. Save a layout first.")%{'folder':SCRIPTSDIR})
            i.props.sensitive = False
            m.add(i)
        else:
            m.add(gtk.MenuItem())

            i = gtk.ImageMenuItem(gtk.STOCK_CLEAR)
            i.connect('activate', lambda menuitem: self.set(""))
            m.add(i)

        m.show_all()
        m.popup(None, None, None, 1, 0)

    def toggle(self, item):
        if item in self.items:
            self.items.remove(item)
        else:
            self.items.append(item)
        if len(self.items) == 0:
            self.set("")
        elif len(self.items) == 1:
            self.set('"%s%s.sh"'%(SCRIPTSDIR, self.items[0]))
        else:
            self.set(CYCLINGPATTERN%{'length':len(self.items), 'countfile':'/tmp/screenlayout_count.%s'%os.environ['USER'], 'cases':" ;; ".join('%d) "%s.sh"'%(i,SCRIPTSDIR+script) for (i,script) in enumerate(self.items))})


def show_keybinder():
    if not gconf:
        d = gtk.MessageDialog(None, gtk.DIALOG_DESTROY_WITH_PARENT, gtk.MESSAGE_ERROR, gtk.BUTTONS_CLOSE)
        d.props.text = _("gconf not available.")
        d.props.secondary_text = _("In order to configure metacity, you need to have the python gconf module installed.")
        d.run()
        d.destroy()
        return

    d = gtk.Window()
    d.props.modal = True
    d.props.title = _("Keybindings (via Metacity)")

    close = gtk.Button(gtk.STOCK_CLOSE)
    close.props.use_stock = True
    close.connect('clicked', lambda *args: d.destroy())
    buttons = gtk.HBox() # FIXME: use HButtonBox
    buttons.props.border_width = 5
    buttons.pack_end(close, expand=False)

    t = MetacityWidget()

    contents = gtk.VBox()
    contents.pack_start(t)
    l = gtk.Label(_('Click on a button in the left column and press a key combination you want to bind to a certain screen layout. (Use backspace to clear accelerators, escape to abort editing.) Then, select one or more layouts in the right column.\n\nThis will only work if you use metacity or another program reading its configuration.'))
    l.props.wrap = True
    contents.pack_start(l)
    contents.pack_end(buttons, expand=False)
    d.add(contents)
    d.show_all()
