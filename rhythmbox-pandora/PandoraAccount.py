from gi import require_version as gi_require_version
gi_require_version("Secret", "1")

from gi.repository import Secret, GObject


class PandoraAccount(object):
    SECRET_SCHEMA = Secret.Schema.new("org.gnome.rhythmbox.plugins.pandora",
                                       Secret.SchemaFlags.NONE,
                                       {})
    instance = None
    
    class __PandoraAccountImpl(GObject.Object):
        def get_credentials(self):
            if not hasattr(self, "__secret"):
                self.__secret = Secret.password_lookup_sync(PandoraAccount.SECRET_SCHEMA,
                                                            {},
                                                            None)

            if self.__secret:
                return tuple(self.__secret.split("\n"))
            else:
                return None, None
                
        
        def set_credentials(self, username, password):
            secret = "\n".join([username, password])
            if secret == self.__secret:
                # Credentials not changed, nothing to do
                return
            self.__secret = secret
            Secret.password_store_sync(PandoraAccount.SECRET_SCHEMA, {}, Secret.COLLECTION_DEFAULT,
                                       "Rhythmbox: Pandora Radio account information",
                                       self.__secret, None)
            self.emit("credentials_changed")
        
        @GObject.Signal
        def credentials_changed(self):
            pass
    
    @classmethod
    def get(cls):
        if not cls.instance:
            cls.instance = cls.__PandoraAccountImpl()
        return cls.instance
