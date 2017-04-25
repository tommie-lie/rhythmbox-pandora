from gi.repository import GObject, Peas

from .PandoraSource import PandoraSource
from .PandoraAccount import PandoraAccount
from pithos import pandora

from concurrent.futures import ThreadPoolExecutor, wait

class PandoraPlugin(GObject.Object, Peas.Activatable):
    object = GObject.property(type=GObject.Object)

    def __init__(self):
        super(PandoraPlugin, self).__init__()
        self.worker = ThreadPoolExecutor(max_workers=1)
        self.pandora_account = PandoraAccount.get()
        self.pandora = self.worker.submit(self.connect, self.pandora_account)

    '''
    Connect to the Pandora radio service using the credentials retrieved from
    account.
    '''
    # if we have more wrapper code of this sort, we are probably better off
    # moving this function to an own module
    def connect(self, account):
        from pithos.pandora.data import client_keys
        
        p = pandora.Pandora()
        username, password = account.get_credentials()
        p.set_audio_quality("highQuality")
        p.connect(client_keys['android-generic'],
                             username, password)
        return p

    def do_activate(self):
        shell = self.object
        self.source = PandoraSource(shell=shell,
                                    plugin=self)

    def do_deactivate(self):
        self.source.delete_thyself()
        self.source = None