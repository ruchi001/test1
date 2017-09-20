parser = SafeConfigParser()
CONFIGURATION_FILE = "Setting.conf"
parser.read(CONFIGURATION_FILE)
port = parser.get('settings', 'PORTREAL')
from ConfigParser import SafeConfigParser