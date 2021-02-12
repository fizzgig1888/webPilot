import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, GdkPixbuf
import os
import json


class server(Gtk.Box):
    def __init__(self, defs):
        Gtk.Box.__init__(self, spacing=8)
        pixbuf = self.svg2pixbuf(defs["icon_loc"])
        gtklab = Gtk.Label()
        gtklab.set_markup("<b>" + defs["name"] + "</b>")
        self.pack_start(pixbuf, False, False, 0)
        self.pack_start(gtklab, False, False, 0)

    def svg2pixbuf(self, loc):
        width = 24
        height = -1
        preserve_aspect_ratio = True
        pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_scale(os.path.dirname(__file__) + loc, width, height, preserve_aspect_ratio)
        image = Gtk.Image()
        image.set_from_pixbuf(pixbuf)
        return image


class WebPilot(Gtk.Window):
    def __init__(self):
        Gtk.Window.__init__(self, title="WebPilot", border_width=10)

        self.grille = Gtk.Grid(row_spacing=8, column_spacing=10)
        self.add(self.grille)

        hbox_ap = self.addserver("Serveur web Apache", "/svg/apache.svg")
        hbox_mdb = self.addserver("Serveur de BDD MariaDB", "/svg/mariadb.svg")
        hbox_njs = self.addserver("API nodeJS", "/svg/nodejs.svg")
        hbox_flk = self.addserver("API Flask", "/svg/flask.svg")

        self.grille.attach(hbox_ap, 0, 0, 1, 1)
        self.grille.attach(hbox_mdb, 0, 1, 1, 1)
        self.grille.attach(hbox_njs, 0, 2, 1, 1)
        self.grille.attach(hbox_flk, 0, 3, 1, 1)

        self.sw_ap = Gtk.Switch()
        self.sw_mdb = Gtk.Switch()
        self.sw_njs = Gtk.Switch()
        self.sw_flk = Gtk.Switch()

        self.grille.attach(self.sw_ap, 1, 0, 1, 1)
        self.grille.attach(self.sw_mdb, 1, 1, 1, 1)
        self.grille.attach(self.sw_njs, 1, 2, 1, 1)
        self.grille.attach(self.sw_flk, 1, 3, 1, 1)

        self.pb = Gtk.ProgressBar()
        self.msg_info = Gtk.Label(label="Test")
        self.btn_test = Gtk.Button(label="Lancer")
        self.btn_test.connect("clicked", self.action_test)

        self.grille.attach(self.pb, 0, 4, 2, 1)
        self.grille.attach(self.msg_info, 0, 5, 2, 1)
        self.grille.attach(self.btn_test, 0, 6, 2, 1)

    def svg2pixbuf(self, loc):
        width = 24
        height = -1
        preserve_aspect_ratio = True
        pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_scale(os.path.dirname(__file__) + loc, width, height, preserve_aspect_ratio)
        image = Gtk.Image()
        image.set_from_pixbuf(pixbuf)
        return image

    def addserver(self, text, iconloc):
        hbox = Gtk.Box(spacing=8)
        pixbuf = self.svg2pixbuf(iconloc)
        gtklab = Gtk.Label()
        gtklab.set_markup("<b>" + text + "</b>")
        hbox.pack_start(pixbuf, False, False, 0)
        hbox.pack_start(gtklab, False, False, 0)
        return hbox

    def action_pb(self):
        self.grille.remove(self.pb)

    def action_test(self, widget):
        print("Action_test")
#        print(os.system('systemctl status apache2'))
        with open("servers.json") as json_file:
            data = json.load(json_file)
            for elt in data['servers']:
                self.serv = server(elt)


if __name__ == "__main__":
    win = WebPilot()
    win.connect("destroy", Gtk.main_quit)
    win.show_all()
    Gtk.main()
