import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, GdkPixbuf
import os
import json

# Anticiper la gestion concurentielle des serveurs
# --> Gestion du port dans JSON
# Modifier le paquet de gestion des serveurs pour reconstuire les fichiers
# depuis un backup.

serverdir = "/home/raphael/Sabayon/git/webPilot/servers"


class server(Gtk.Box):
    def __init__(self, path, data):
        self.carac = data
        Gtk.Box.__init__(self, spacing=8)
        pixbuf = self.svg2pixbuf(os.path.join(path, self.carac["icon_loc"]))
        gtklab = Gtk.Label()
        gtklab.set_markup("<b>" + self.carac["name"] + "</b>")
        self.pack_start(pixbuf, False, False, 0)
        self.pack_start(gtklab, False, False, 0)
        self.cursor_state = Gtk.Switch()
        self.cursor_state.connect("notify::active", self.test)
        self.cursor_state.set_active(self.isserverrunning())
        self.pack_start(self.cursor_state, False, False, 0)

    def svg2pixbuf(self, loc):
        width = 24
        height = -1
        preserve_aspect_ratio = True
        pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_scale(loc, width, height,
                                                         preserve_aspect_ratio)
        image = Gtk.Image()
        image.set_from_pixbuf(pixbuf)
        return image

    def isserverrunning(self):
        systemctlstatus = os.system(self.carac["status_command"])
        return (systemctlstatus == 0)

    def test(self, switch, gparam):
        print(self.isserverrunning())
        if switch.get_active():
            state = "on"
        else:
            state = "off"
        print("Switch was turned", state)


class webPilot(Gtk.Window):
    line = 0

    def __init__(self):
        Gtk.Window.__init__(self, title="WebPilot", border_width=10)
        self.grille = Gtk.Grid(row_spacing=8, column_spacing=10)
        self.add(self.grille)
        self.populate_servers(serverdir)
        self.addstuff()

    def populate_servers(self, json_path):
        for diritem in os.scandir(json_path):
            if (diritem.path.endswith(".json") and diritem.is_file()):
                with open(diritem.path) as json_data:
                    data = json.load(json_data)
                    self.grille.attach(server(json_path, data), 0,
                                       self.line, 2, 1)
                    self.line += 1

    def addstuff(self):
        self.pb = Gtk.ProgressBar()
        self.grille.attach(self.pb, 0, self.line, 2, 1)
        self.line += 1
        self.msg_info = Gtk.Label(label="Test")
        self.grille.attach(self.msg_info, 0, self.line, 2, 1)
        self.line += 1
        self.btn_test = Gtk.Button(label="Lancer")
        self.grille.attach(self.btn_test, 0, self.line, 2, 1)
        self.line += 1


if __name__ == "__main__":
    win = webPilot()
    win.connect("destroy", Gtk.main_quit)
    win.show_all()
    Gtk.main()
