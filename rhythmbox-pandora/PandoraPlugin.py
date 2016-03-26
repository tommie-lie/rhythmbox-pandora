from gi.repository import GObject, Peas

from .PandoraSource import PandoraSource

class PandoraPlugin(GObject.Object, Peas.Activatable):
    object = GObject.property(type=GObject.Object)

    def __init__(self):
        super(PandoraPlugin, self).__init__()

    def do_activate(self):
        shell = self.object
        self.source = PandoraSource(shell=shell)

    def do_deactivate(self):
        self.source.delete_thyself()
        self.source = None