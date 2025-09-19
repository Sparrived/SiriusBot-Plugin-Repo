from ncatbot.utils import get_log
from ncatbot.plugin_system import NcatBotPlugin

class SiriusPlugin(NcatBotPlugin):
    def __init__(self, *args, **kwargs) :
        NcatBotPlugin.__init__(self, *args, **kwargs)
        self.author = "Sparrived"
        self.dependencies = {"SiriusCore" : ">=1.0.0"}
        self._log = get_log(self.name)

    def on_load(self) -> None:
        self._log.name = self.name
        