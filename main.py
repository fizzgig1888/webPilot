from pystemd.systemd1 import Unit, Manager
import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, GdkPixbuf, GLib
import os
import json
import time
import threading

# Faire un peu de déco : logo EN. Virer barre ?
# Régler le cas d'un service qui plante.

serverdir = "/home/raphael/Sabayon/git/webPilot/servers"
exiting = False


class Services(Manager):
    lst = []

    def __init__(self, *args, **kwargs):
        Manager.__init__(self, *args, **kwargs)
        self.load()

    def add_service(self, service):
        self.lst += service

    def enable_services(self):
        self.Manager.EnableUnitFiles(self.lst, False, True)

    def disable_services(self):
        self.Manager.DisableUnitFiles(self.lst, False)


class server(Gtk.Box):
    events = "UI_only"
    dog = False
    startdelay = 10
    stopdelay = 10
    threshold = 0.2
    dogdelay = 1
    AskedState = b'inactive'
    recordedPID = -1
    recordedBtnState = False

    def __init__(self, path, data, logbox):
        self.carac = data
        self.logbox = logbox
        self.unit = Unit(self.carac["service_name"], _autoload=True)
        self.service = self.unit.Unit
        serv.add_service([self.carac["service_name"]])
        Gtk.Box.__init__(self, spacing=8)
        pixbuf = self.svg2pixbuf(os.path.join(path, self.carac["icon_loc"]))
        gtklab = Gtk.Label()
        gtklab.set_markup("<b>" + self.carac["name"] + "</b>")
        self.pack_start(pixbuf, False, False, 0)
        self.pack_start(gtklab, False, False, 0)
        self.cursor_state = Gtk.Switch()
        self.cursor_state.connect("notify::active", self.changeserverstate)
        self.pack_start(self.cursor_state, False, False, 0)
        self.server_check()
        self.events = "Active"

    def server_check(self):
        if self.service.ActiveState == b'active':
            self.AskedState = b'active'
            self.cursor_state.set_active(True)
            self.dog = True
            threading.Thread(target=self.watchdog_surveil).start()

    def server_failed2run(self):
        self.logbox.info("Arrêt inatendu de : " + self.carac["name"], 30)
        self.events = "Inactive"
        self.cursor_state.set_state(False)
        self.events = "Active"

    def server_failed2stop(self):
        if self.service.ActiveState == b'active':
            self.logbox.info("Erreur à l'arrêt de : " + self.carac["name"] + ".\nLe service est toujours actif !", 30)
            self.AskedState = b'active'
            renew_surveil = True
            self.events = "UI_only"
            self.cursor_state.set_state(True)
        else:
            self.logbox.info("Erreur à l'arrêt de : " + self.carac["name"] + "\nLe service est dans un état inconnu !", 30)
        self.events = "Active"

    def watchdog_surveil(self):
        print("watchdog " + self.carac["service_name"] + " démarre")
        renew_surveil = True
        while renew_surveil:
            renew_surveil = False
            while self.dog and self.service.ActiveState == self.AskedState: # A modifier pour que le deactivating et inactive concordent.
                time.sleep(self.dogdelay)
                print("watchdog " + self.carac["service_name"])
                if exiting or not self.dog:
                    return
            if self.service.ActiveState != b'active' and self.AskedState == b'active':
                self.server_failed2run()
#            elif self.AskedState == b'inactive' and self.service.ActiveState != b'inactive':
#                self.server_failed2stop()

    def start_server(self):
        self.AskedState = b'active'
        self.service.Start(b'replace')
        self.logbox.info("Tentative de démarrage de : " + self.carac["name"], self.startdelay)
        i = 0
        while i < self.startdelay/self.threshold and (self.service.ActiveState != b'active' or self.unit.MainPID != self.recordedPID or self.unit.MainPID == 0):
            time.sleep(self.threshold)
            self.recordedPID = self.unit.MainPID
            i += 1
        if self.service.ActiveState == b'active':
            self.logbox.info("Démarrage réussi de : " + self.carac["name"], 1)
            self.events = "Active"
            self.dog = True
            self.watchdog_surveil()
        else:
            self.logbox.info("Echec du démarrage de : " + self.carac["name"], 2)
            self.dog = False
            self.events = "UI_only"
            self.cursor_state.set_active(False)
            self.events = "Active"

    def stop_server(self):
        # penser à bloquer le curseur ...
        self.AskedState = b'inactive'
        self.dog = False
        self.service.Stop(b'replace')
        self.logbox.info("Tentative d'arrêt de : " + self.carac["name"], self.stopdelay)
        i = 0
        while i < self.stopdelay/self.threshold and (self.service.ActiveState == b'deactivating' or self.unit.MainPID != 0):
            print("looping : " + str(self.service.ActiveState))
            time.sleep(self.threshold)
            i += 1
        self.events = "UI_only"
        if self.service.ActiveState == b'inactive':
            self.logbox.info("Arrêt réussi de : " + self.carac["name"], 1)
            self.events = "Active"
        else:
            self.server_failed2stop()
        print("stop_server fini")

    def svg2pixbuf(self, loc):
        width = 24
        height = -1
        preserve_aspect_ratio = True
        pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_scale(loc, width, height,
                                                         preserve_aspect_ratio)
        image = Gtk.Image()
        image.set_from_pixbuf(pixbuf)
        return image

    def debugging(self):
        print(self.service.ActiveState)
        print(self.service.SubState)
        print(self.unit.MainPID)

    def changeserverstate(self, switch, gparam):
        if self.events == "Inactive":
            switch.set_active(self.recordedBtnState)
            print("locked")
            return
        elif self.events == "UI_only":
            print("no effect")
            return
        self.recordedBtnState = switch.get_active()
        self.events = "Inactive"
        if switch.get_active():
            threading.Thread(target=self.start_server).start()
        else:
            threading.Thread(target=self.stop_server).start()


class logBox(Gtk.Label):
    id = -1

    def info(self, txt, delay):
        None
        if self.id != -1:
            GLib.source_remove(self.id)
#        self.set_text(txt)
        GLib.idle_add(self.set_text, txt)
        self.id = GLib.timeout_add_seconds(delay, self.clear)

    def clear(self):
        self.set_text("")
        self.id = -1

class webPilot(Gtk.Window):
    def defstuff(self):
        self.line = 0
        self.pb = Gtk.ProgressBar()
        self.grille = Gtk.Grid(row_spacing=8, column_spacing=10)
        self.logbox = logBox(label="Bienvenue dans webPilot!")

    def __init__(self):
        self.defstuff()
        Gtk.Window.__init__(self, title="webPilot", border_width=10)
        self.add(self.grille)
        self.populate_servers(serverdir)
        self.addstuff()

    def populate_servers(self, json_path):
        for diritem in os.scandir(json_path):
            if (diritem.path.endswith(".json") and diritem.is_file()):
                with open(diritem.path) as json_data:
                    data = json.load(json_data)
                    self.grille.attach(server(json_path, data, self.logbox), 0, self.line, 2, 1)
                    self.line += 1

    def addstuff(self):
        self.grille.attach(self.pb, 0, self.line, 2, 1)
        self.line += 1
        self.grille.attach(self.logbox, 0, self.line, 2, 1)
        self.line += 1


def close_threads_and_services(dummy):
    global exiting
    global win
    exiting = True
    serv.disable_services()
    win.destroy()
    Gtk.main_quit()


if __name__ == "__main__":
    serv = Services()
    win = webPilot()
    print(serv.enable_services())
    win.connect("destroy", close_threads_and_services)
    win.show_all()
    Gtk.main()
