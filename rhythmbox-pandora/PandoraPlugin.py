from gi.repository import GObject, Peas

from .PandoraSource import PandoraSource
from .PandoraAccount import PandoraAccount
from pithos import pandora
from pithos.pandora.data import client_keys as pandora_client_keys

class PandoraPlugin(GObject.Object, Peas.Activatable):
    object = GObject.property(type=GObject.Object)

    def __init__(self):
        super(PandoraPlugin, self).__init__()
        self.pandora_account = PandoraAccount.get()
        
        username, password = self.pandora_account.get_credentials()
        self.pandora = pandora.Pandora()
        self.pandora.connect(pandora_client_keys['android-generic'], username, password)

    def do_activate(self):
        shell = self.object
        self.source = PandoraSource(shell=shell,
                                    plugin=self)

    def do_deactivate(self):
        self.source.delete_thyself()
        self.source = None