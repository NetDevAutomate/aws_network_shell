"""Shell command handlers organized by domain."""

from .root import RootHandlersMixin
from .cloudwan import CloudWANHandlersMixin
from .vpc import VPCHandlersMixin
from .tgw import TGWHandlersMixin
from .ec2 import EC2HandlersMixin
from .firewall import FirewallHandlersMixin
from .vpn import VPNHandlersMixin
from .elb import ELBHandlersMixin
from .utilities import UtilityHandlersMixin

__all__ = [
    "RootHandlersMixin",
    "CloudWANHandlersMixin",
    "VPCHandlersMixin",
    "TGWHandlersMixin",
    "EC2HandlersMixin",
    "FirewallHandlersMixin",
    "VPNHandlersMixin",
    "ELBHandlersMixin",
    "UtilityHandlersMixin",
]
