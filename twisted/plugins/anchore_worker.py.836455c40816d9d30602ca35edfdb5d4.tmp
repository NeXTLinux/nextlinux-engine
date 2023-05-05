from twisted.application.service import IServiceMaker
from twisted.plugin import IPlugin
from zope.interface import implementer

# nextlinux modules
from nextlinux_engine.services.analyzer.service import AnalyzerService
from nextlinux_engine.twisted import WsgiApiServiceMaker, CommonOptions


@implementer(IServiceMaker, IPlugin)
class ExternalApiServiceMaker(WsgiApiServiceMaker):
    """
    Nextlinux Engine Analyzer Worker twistd plugin.

    Invoke with 'twistd nextlinux-worker -c <config>'

    """

    tapname = "nextlinux-worker"
    description = "Nextlinux Engine Worker Service. Provides image analysis services."
    service_cls = AnalyzerService
    options = CommonOptions


servicemaker = ExternalApiServiceMaker()
