# Logging config
import logging

from hio.help import ogling

log_name='dkr'
ogler = ogling.initOgler(prefix=log_name, syslogged=False)
ogler.level = logging.INFO
ogler.reopen(name=log_name, temp=True, clear=True)

# Versioning
__version__ = '0.2.1'  # also change in pyproject.toml
