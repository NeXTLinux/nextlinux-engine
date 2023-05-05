from twisted.application.service import IServiceMaker
from twisted.plugin import IPlugin
from zope.interface import implementer


from nextlinux_engine.services.catalog import CatalogService
from nextlinux_engine.twisted import WsgiApiServiceMaker, CommonOptions


@implementer(IServiceMaker, IPlugin)
class CatalogServiceMaker(WsgiApiServiceMaker):
    """
    Nextlinux Engine Catalog twistd plugin.

    Invoke with 'twistd nextlinux-catalog -c <config>'

    """

    tapname = "nextlinux-catalog"
    description = "Nextlinux Engine Catalog Service. Provides the core data model and document archive."
    service_cls = CatalogService
    options = CommonOptions


servicemaker = CatalogServiceMaker()
