import sys
import os

relative_path = os.path.dirname(sys.modules[__name__].__file__)
RSRC_DIR = os.path.join(relative_path,'rsrc')
SUPPORTED_JAVA=os.path.join('/usr/share/lliurex-java-panel','supported-javas')
BANNERS=os.path.join('/usr/share/lliurex-java-panel','banners')
TEXT_DOMAIN = "lliurex-java-panel"
ICONS_THEME="/usr/share/icons/breeze/actions/32"
