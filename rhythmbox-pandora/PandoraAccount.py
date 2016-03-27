from gi import require_version as gi_require_version
gi_require_version("Secret", "1")

from gi.repository import Secret


class PandoraAccount(object):
    SECRET_SCHEMA = Secret.Schema.new("org.gnome.rhythmbox.plugins.pandora",
                                       Secret.SchemaFlags.NONE,
                                       {})
    instance = None
    
    class __PandoraAccountImpl(object):
        def __init__(self):
            def on_password_lookup(source, result):
                __secret = Secret.password_lookup_finish(result)
            
            self.__secret = None
            secret_service = Secret.password_lookup(PandoraAccount.SECRET_SCHEMA, {}, None,
                                                    on_password_lookup)
        
        def get_credentials(self):
            if self.__secret:
                return tuple(self.__secret.split("\n"))
            return None, None
        
        def set_credentials(self, username, password):
            def on_password_store(source, result):
                Secret.password_store_finish(result)
            
            secret = "\n".join([username, password])
            if secret == self.__secret:
                # Credentials not changed, nothing to do
                return
            self.__secret = secret
            Secret.password_store(PandoraAccount.SECRET_SCHEMA, {}, Secret.COLLECTION_DEFAULT,
                                  "Rhythmbox: Pandora Radio account information",
                                  self.__secret, None, on_password_store)
    
    @classmethod
    def get(cls):
        if not cls.instance:
            cls.instance = cls.__PandoraAccountImpl()
        return cls.instance
