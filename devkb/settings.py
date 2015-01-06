import os
import os.path

CONF_PATH = os.environ.get('DEVKB_CONF', '/etc/devkb')

DATABASE = os.path.join(CONF_PATH, 'db.yml')

LOG_FILE = 'devel.log'

LOG_LEVEL = 'DEBUG'
