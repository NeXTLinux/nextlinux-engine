"""
twistd plugin for running the nextlinux-api service. Contains service and cli options code.

e.g.
twistd nextlinux-api -c /config

"""

from twisted.application.service import IServiceMaker
from twisted.plugin import IPlugin
from zope.interface import implementer

from nextlinux_engine.services.apiext import ExternalApiService
from nextlinux_engine.twisted import WsgiApiServiceMaker, CommonOptions


@implementer(IServiceMaker, IPlugin)
class ExternalApiServiceMaker(WsgiApiServiceMaker):
    """
    Nextlinux External API twistd plugin.

    Invoke with 'twistd nextlinux-api -c <config>'

    """

    tapname = "nextlinux-api"
    description = "Nextlinux Engine External API Service. Provides the user-facing API."
    service_cls = ExternalApiService
    options = CommonOptions


servicemaker = ExternalApiServiceMaker()
