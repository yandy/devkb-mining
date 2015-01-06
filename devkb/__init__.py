import time
import logging
import devkb.settings

_settings = vars(devkb.settings)

_logformat = _settings.get(
    'LOG_FORMAT', '%(asctime)-15s [%(levelname)s] %(message)s')
_logfilename = _settings.get(
    'LOG_FILE', '/var/log/devkb/%3.f.log' % time.time())
_loglevel = _settings.get('LOG_LEVEL', 'INFO')

logging.basicConfig(format=_logformat, filename=_logfilename, level=_loglevel)
