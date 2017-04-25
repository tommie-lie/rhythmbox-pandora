from gi.repository import GObject, PeasGtk, Gtk
import rb

from .PandoraAccount import PandoraAccount

class PandoraConfig(GObject.Object, PeasGtk.Configurable):
    def __init__(self):
        super(PandoraConfig, self).__init__()
        self.builder = Gtk.Builder() 
    
    def do_create_configure_widget(self):
        self.builder.add_from_file(rb.find_plugin_file(self, "data/pandora-prefs.ui"))
        self.builder.connect_signals(self)
        
        (username, password) = PandoraAccount.get().get_credentials()
        username_entry = self.builder.get_object("username-entry")
        username_entry.set_text(username)
        password_entry = self.builder.get_object("password-entry")
        password_entry.set_text(password)

        return self.builder.get_object("pandora-prefs")
    
    def on_login_data_changed(self, widget, event):
        username = self.builder.get_object("username-entry").get_text()
        password = self.builder.get_object("password-entry").get_text()
        PandoraAccount.get().set_credentials(username, password)