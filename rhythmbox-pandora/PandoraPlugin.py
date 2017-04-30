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

    '''
    Connect to the Pandora radio service using the credentials retrieved from
    account.
    '''
    # if we have more wrapper code of this sort, we are probably better off
    # moving this function to an own module
    def connect_pandora(self, credentials):
        from pithos.pandora.data import client_keys
        
        username, password = credentials
        self.pandora.set_audio_quality(self.settings["audio-quality"])
        self.pandora.connect(client_keys['android-generic'],
                             username, password)
        self.emit("connected")

    def do_activate(self):
        self.worker = ThreadPoolExecutor(max_workers=1)
        self.pandora = pandora.Pandora()
        self.settings = PandoraSettings(self)
        
        self._signal_handlers = []
        self._signal_handlers.append((self.settings, self.settings.connect("changed::audio-quality", self.on_audio_quality_changed)))
        self._signal_handlers.append((PandoraAccount.get(), PandoraAccount.get().connect("credentials_changed", self.on_credentials_changed)))
        self.on_credentials_changed(PandoraAccount.get())

    def do_deactivate(self):
        for object, handler_id in self._signal_handlers:
            object.disconnect(handler_id)
        self._signal_handlers = None
        
        self.source.delete_thyself()
        self.source = None
        self.pandora = None
        self.worker.shutdown()
        self.worker = None

    def on_credentials_changed(self, account):
        if hasattr(self, "source") and self.source:
            self.source.delete_thyself()
        self.source = PandoraSource(shell=self.object,
                                       plugin=self)
        self.worker.submit(self.connect_pandora, account.get_credentials)
    
    def on_audio_quality_changed(self, settings, key):
        self.pandora.set_audio_quality(settings["audio-quality"])