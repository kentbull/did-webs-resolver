# Logging config
import logging
from hio.help import ogling

ogler = ogling.initOgler(prefix='dkr', syslogged=False)
ogler.level = logging.INFO
ogler.reopen(name='dkr', temp=True, clear=True)

# Versioning
__version__ = "0.2.1" # also change in pyproject.toml
