from twisted.application.service import IServiceMaker
from twisted.plugin import IPlugin
from zope.interface import implementer

# nextlinux modules
from nextlinux_engine.services.policy_engine import PolicyEngineService
from nextlinux_engine.twisted import WsgiApiServiceMaker, CommonOptions


@implementer(IServiceMaker, IPlugin)
class PolicyEngineServiceMaker(WsgiApiServiceMaker):
    """
    Nextlinux Engine Policy Engine twistd plugin.

    Invoke with 'twistd nextlinux-policy-engine -c <config>'

    """

    tapname = "nextlinux-policy-engine"
    description = (
        "Nextlinux Engine Policy Engine Service. Provides policy evaluation service."
    )
    service_cls = PolicyEngineService
    options = CommonOptions


servicemaker = PolicyEngineServiceMaker()
