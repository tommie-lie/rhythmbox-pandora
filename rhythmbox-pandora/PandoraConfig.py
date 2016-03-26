from gi.repository import GObject, PeasGtk, Gtk

class PandoraConfig(GObject.Object, PeasGtk.Configurable):
    object = GObject.property(type=GObject.Object)
    
    def __init__(self):
        super(PandoraConfig, self).__init__()
    
    def do_create_configure_widget(self):
        return None