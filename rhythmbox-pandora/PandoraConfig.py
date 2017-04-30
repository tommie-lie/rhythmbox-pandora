from gi.repository import GObject, PeasGtk, Gtk, Gio
import rb

from .PandoraAccount import PandoraAccount

class PandoraSettings(Gio.Settings):
    def __init__(self, plugin):
        path = rb.find_plugin_file(plugin, "data/")
        schema_source = Gio.SettingsSchemaSource.new_from_directory(path, Gio.SettingsSchemaSource.get_default(), False)
        schema = schema_source.lookup("org.gnome.rhythmbox.plugins.pandora", True)
        super(PandoraSettings, self).__init__(settings_schema = schema)
    
    # todo: implement unbind for the following method and submit to PyGObject
    def bind_with_convert(self, key, widget, prop, key_to_prop, prop_to_key):
        """Recreate g_settings_bind_with_mapping from scratch.
  
        This method was shamelessly stolen from John Stowers'
        gnome-tweak-tool on May 14, 2012 and improved by Thomas Liebetraut
        """
        property_changed_id = None
        setting_changed_id = None
        def setting_changed(settings, key):
            """Update widget property."""
            widget.handler_block(property_changed_id)
            widget.set_property(prop, key_to_prop(settings[key]))
            widget.handler_unblock(property_changed_id)
  
        def property_changed(widget, param):
            """Update GSettings key."""
            self.handler_block(setting_changed_id)
            self[key] = prop_to_key(widget.get_property(prop))
            self.handler_unblock(setting_changed_id)
  
        setting_changed_id = self.connect('changed::' + key, setting_changed)
        property_changed_id = widget.connect('notify::' + prop, property_changed)
        setting_changed(self, key)  # init default state



class PandoraConfig(GObject.Object, PeasGtk.Configurable):
    def do_create_configure_widget(self):
        self.settings = PandoraSettings(self)

        self.builder = Gtk.Builder() 
        self.builder.add_from_file(rb.find_plugin_file(self, "data/pandora-prefs.ui"))
        self.builder.connect_signals(self)
        
        (username, password) = PandoraAccount.get().get_credentials()
        username_entry = self.builder.get_object("username-entry")
        username_entry.set_text(username)
        password_entry = self.builder.get_object("password-entry")
        password_entry.set_text(password)
        
        quality_combobox = self.builder.get_object("audio-quality-combobox")
        
        def quality_to_combobox(quality):
            for row in quality_combobox.get_model():
                if row[1] == quality:
                    return row.path[0]
        
        def combobox_to_quality(idx):
            return quality_combobox.get_model()[idx][1]
        
        self.settings.bind_with_convert("audio-quality", quality_combobox, "active", quality_to_combobox, combobox_to_quality)

        return self.builder.get_object("pandora-prefs")
    
    def on_login_data_changed(self, widget, event):
        username = self.builder.get_object("username-entry").get_text()
        password = self.builder.get_object("password-entry").get_text()
        PandoraAccount.get().set_credentials(username, password)