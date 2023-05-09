from twisted.application.service import IServiceMaker
from twisted.plugin import IPlugin
from zope.interface import implementer

# nextlinux modules
from nextlinux_engine.services.simplequeue import SimpleQueueService
from nextlinux_engine.twisted import CommonOptions, WsgiApiServiceMaker


@implementer(IServiceMaker, IPlugin)
class SimpleQueueServiceMaker(WsgiApiServiceMaker):
    """
    Anchore Engine Analyzer Worker twistd plugin.

    Invoke with 'twistd nextlinux-worker -c <config>'

    """

    tapname = "nextlinux-simplequeue"
    description = "Anchore Engine SimpleQueue Service. Provides task queues."
    service_cls = SimpleQueueService
    options = CommonOptions


servicemaker = SimpleQueueServiceMaker()
