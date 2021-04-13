from pystemd.systemd1 import Unit
from pystemd.systemd1 import Manager


class Services(Manager):
    def __init__(self, *args, **kwargs):
        Manager.__init__(self, *args, **kwargs)
        self.load()


m = Services()
print(m.Manager.ListUnitFiles())
