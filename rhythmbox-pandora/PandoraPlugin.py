from gi.repository import GObject, Peas

from .PandoraSource import PandoraSource
from .PandoraAccount import PandoraAccount
from .PandoraConfig import PandoraSettings
from pithos import pandora

from concurrent.futures import ThreadPoolExecutor, wait

class PandoraPlugin(GObject.Object, Peas.Activatable):
    object = GObject.property(type=GObject.Object)
    
    __gsignals__ = {
        "connected": (GObject.SIGNAL_RUN_FIRST, None, ())
    }

    def __init__(self):
        super(PandoraPlugin, self).__init__()
        self.worker = ThreadPoolExecutor(max_workers=1)
        self.pandora = pandora.Pandora()

    '''
    Connect to the Pandora radio service using the credentials retrieved from
    account.
    '''
    # if we have more wrapper code of this sort, we are probably better off
    # moving this function to an own module
    def connect_pandora(self):
        from pithos.pandora.data import client_keys
        
        account = PandoraAccount.get()
        username, password = account.get_credentials()
        self.pandora.set_audio_quality(self.settings["audio-quality"])
        self.pandora.connect(client_keys['android-generic'],
                             username, password)
        self.emit("connected")

    def do_activate(self):
        self.settings = PandoraSettings(self)
        self.settings.connect("changed::audio-quality", self.on_audio_quality_changed)
        PandoraAccount.get().connect("credentials_changed", self.on_credentials_changed)
        self.source = PandoraSource(shell=self.object,
                                    plugin=self)
        self.worker.submit(self.connect_pandora)

    def do_deactivate(self):
        self.source.delete_thyself()
        self.source = None
    
    def on_credentials_changed(self, account):
        self.source.delete_thyself()
        self.source = PandoraSource(shell=self.object,
                                    plugin=self)
        self.worker.submit(self.connect_pandora)
    
    def on_audio_quality_changed(self, settings, key):
        self.pandora.set_audio_quality(settings["audio-quality"])