import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, GdkPixbuf
import os
import json

# Question à se poser : peut-on laisser tourner un serveur en arrière plan, qui ne soit pas référencé sur systemctl ?
# La réponse est oui, mais il risque d'y avoir tout un tas de problématiques.
# Il vaut surement mieux créer des fichiers de conf à ajouter à systemd, pour démarrer le truc.
# Anticiper la gestion concurentielle des serveurs.
# Modifier le paquet de gestion des serveurs pour reconstuire les fichiers depuis un backup.

class server(Gtk.Box):
    def __init__(self, defs):
        Gtk.Box.__init__(self, spacing=8)
        pixbuf = self.svg2pixbuf(defs["icon_loc"])
        gtklab = Gtk.Label()
        gtklab.set_markup("<b>" + defs["name"] + "</b>")
        self.pack_start(pixbuf, False, False, 0)
        self.pack_start(gtklab, False, False, 0)
        self.cursor_state = Gtk.Switch()
        self.cursor_state.connect("notify::active", self.test)
        self.pack_start(self.cursor_state, False, False, 0)

    def svg2pixbuf(self, loc):
        width = 24
        height = -1
        preserve_aspect_ratio = True
        pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_scale(os.path.dirname(__file__) + loc, width, height, preserve_aspect_ratio)
        image = Gtk.Image()
        image.set_from_pixbuf(pixbuf)
        return image

    def test(self, switch, gparam):
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
        self.populate_servers("servers.json")
        self.addstuff()

    def populate_servers(self, json_path):
        with open(json_path) as json_file:
            data = json.load(json_file)
            for elt in data['servers']:
                self.grille.attach(server(elt), 0, self.line, 2, 1)
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
