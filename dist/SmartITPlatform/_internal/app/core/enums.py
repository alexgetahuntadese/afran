from enum import StrEnum


class PlanCode(StrEnum):
    TRIAL = "trial"
    PROFESSIONAL = "professional"
    ENTERPRISE = "enterprise"


class SubscriptionStatus(StrEnum):
    ACTIVE = "active"
    EXPIRED = "expired"
    SUSPENDED = "suspended"
    CANCELLED = "cancelled"


class DeviceType(StrEnum):
    PC = "pc"
    LAPTOP = "laptop"
    PRINTER = "printer"
    ZEBRA_PRINTER = "zebra_printer"
    THERMAL_PRINTER = "thermal_printer"
    ROUTER = "router"
    SWITCH = "switch"
    SERVER = "server"
    UNKNOWN = "unknown"


class DeviceStatus(StrEnum):
    ONLINE = "online"
    OFFLINE = "offline"
    DEGRADED = "degraded"


class AlertSeverity(StrEnum):
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"


class AlertStatus(StrEnum):
    OPEN = "open"
    ACKNOWLEDGED = "acknowledged"
    RESOLVED = "resolved"


class RemoteSessionStatus(StrEnum):
    REQUESTED = "requested"
    APPROVED = "approved"
    ACTIVE = "active"
    ENDED = "ended"
    DENIED = "denied"


class PaymentProvider(StrEnum):
    CHAPA = "chapa"
    TELEBIRR = "telebirr"
    SANTIMPAY = "santimpay"
