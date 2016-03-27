import sys
sys.path.append("/usr/share/pithos")

from .PandoraPlugin import PandoraPlugin
from .PandoraConfig import PandoraConfig

__all__ = ["PandoraPlugin", "PandoraConfig"]
