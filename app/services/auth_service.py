from datetime import UTC, datetime

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.enums import AlertSeverity, AlertStatus, DeviceStatus, DeviceType, PlanCode
from app.core.security import create_access_token, hash_password, verify_password
from app.models import Alert, Branch, Device, Organization, Printer, Role, Subscription, User
from app.schemas.auth import TokenResponse, UserCreate


class AuthService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def bootstrap_owner(self, data: UserCreate) -> TokenResponse:
        existing = await self.session.execute(select(User).where(User.email == data.email))
        if existing.scalar_one_or_none():
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email already registered")

        organization = Organization(name=data.organization_name, industry="healthcare_office")
        role = Role(
            name=f"{data.organization_name}:owner",
            permissions={
                "devices": ["read", "write"],
                "printers": ["read", "write", "admin"],
                "remote_support": ["start", "control"],
                "subscriptions": ["read", "write"],
                "alerts": ["read", "acknowledge", "resolve"],
            },
        )
        self.session.add_all([organization, role])
        await self.session.flush()

        branch = Branch(
            organization_id=organization.id,
            name=data.branch_name,
            subnet_cidr=None,
        )
        user = User(
            organization_id=organization.id,
            role_id=role.id,
            email=data.email,
            full_name=data.full_name,
            password_hash=hash_password(data.password),
        )
        subscription = Subscription(
            organization_id=organization.id,
            plan_code=PlanCode.PROFESSIONAL,
            trial_ends_at=None,
            device_limit=None,
            feature_flags={
                "unlimited_devices": True,
                "remote_support": True,
                "advanced_monitoring": True,
                "automation_scripts": True,
                "cloud_sync": False,
                "label": "Professional",
            },
        )
        self.session.add_all([branch, user, subscription])
        await self.session.commit()
        return self._token_for_user(user)

    async def login(self, email: str, password: str) -> TokenResponse:
        result = await self.session.execute(select(User).where(User.email == email, User.is_active.is_(True)))
        user = result.scalar_one_or_none()
        if not user or not verify_password(password, user.password_hash):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
        return self._token_for_user(user)

    async def demo_workspace(self) -> TokenResponse:
        email = "demo@smartit.example.com"
        password = "demo12345"
        result = await self.session.execute(select(User).where(User.email == email, User.is_active.is_(True)))
        user = result.scalar_one_or_none()
        if user is None:
            token = await self.bootstrap_owner(
                UserCreate(
                    organization_name="Demo Hospital Operations",
                    branch_name="Main Branch",
                    email=email,
                    full_name="Demo Operator",
                    password=password,
                )
            )
            user = await self.session.get(User, token.user_id)
            if user is None:
                raise RuntimeError("Demo user was not created")

        await self._seed_demo_data(user)
        await self.session.commit()
        return self._token_for_user(user)

    async def _seed_demo_data(self, user: User) -> None:
        branch_result = await self.session.execute(
            select(Branch).where(Branch.organization_id == user.organization_id).order_by(Branch.created_at)
        )
        branch = branch_result.scalars().first()
        if branch is None:
            branch = Branch(organization_id=user.organization_id, name="Main Branch", subnet_cidr="192.168.1.0/24")
            self.session.add(branch)
            await self.session.flush()

        devices = [
            {
                "hostname": "nurse-station-01",
                "ip_address": "192.168.1.24",
                "mac_address": "00:1A:2B:3C:4D:24",
                "vendor": "Dell",
                "operating_system": "Windows",
                "device_type": DeviceType.PC,
                "status": DeviceStatus.ONLINE,
                "latency_ms": 8,
                "department": "Nursing",
                "floor": "1",
            },
            {
                "hostname": "lab-printer-01",
                "ip_address": "192.168.1.45",
                "mac_address": "00:1A:2B:3C:4D:45",
                "vendor": "HP",
                "operating_system": None,
                "device_type": DeviceType.PRINTER,
                "status": DeviceStatus.DEGRADED,
                "latency_ms": 18,
                "department": "Laboratory",
                "floor": "2",
            },
            {
                "hostname": "billing-terminal-02",
                "ip_address": "192.168.1.61",
                "mac_address": "00:1A:2B:3C:4D:61",
                "vendor": "Lenovo",
                "operating_system": "Windows",
                "device_type": DeviceType.PC,
                "status": DeviceStatus.OFFLINE,
                "latency_ms": None,
                "department": "Billing",
                "floor": "1",
            },
        ]
        created_devices: dict[str, Device] = {}
        for data in devices:
            result = await self.session.execute(
                select(Device).where(Device.branch_id == branch.id, Device.ip_address == data["ip_address"])
            )
            device = result.scalar_one_or_none()
            if device is None:
                device = Device(organization_id=user.organization_id, branch_id=branch.id, **data)
                self.session.add(device)
            else:
                for key, value in data.items():
                    setattr(device, key, value)
            if device.status == DeviceStatus.ONLINE:
                device.last_seen_at = datetime.now(UTC)
            created_devices[data["hostname"]] = device
        await self.session.flush()

        printer_result = await self.session.execute(
            select(Printer).where(Printer.branch_id == branch.id, Printer.name == "Lab HP LaserJet")
        )
        printer = printer_result.scalar_one_or_none()
        if printer is None:
            printer = Printer(
                organization_id=user.organization_id,
                branch_id=branch.id,
                name="Lab HP LaserJet",
            )
            self.session.add(printer)
        printer.model = "HP LaserJet Pro"
        printer.driver_name = "HP Universal Printing"
        printer.ip_address = "192.168.1.45"
        printer.department = "Laboratory"
        printer.floor = "2"
        printer.status = "warning"
        printer.health_score = 72
        printer.queue_depth = 12
        printer.toner_level = 14
        printer.paper_status = "low"
        printer.last_checked_at = datetime.now(UTC)
        await self.session.flush()

        alert_result = await self.session.execute(
            select(Alert).where(
                Alert.organization_id == user.organization_id,
                Alert.title == "Lab printer needs attention",
                Alert.status == AlertStatus.OPEN,
            )
        )
        if alert_result.scalar_one_or_none() is None:
            self.session.add(
                Alert(
                    organization_id=user.organization_id,
                    branch_id=branch.id,
                    device_id=created_devices["lab-printer-01"].id,
                    printer_id=printer.id,
                    severity=AlertSeverity.WARNING,
                    status=AlertStatus.OPEN,
                    title="Lab printer needs attention",
                    message="Queue depth is high and toner is below the operating threshold.",
                    evidence={"queue_depth": 12, "toner_level": 14},
                )
            )

    def _token_for_user(self, user: User) -> TokenResponse:
        token = create_access_token(
            str(user.id),
            {"organization_id": str(user.organization_id), "role_id": str(user.role_id) if user.role_id else None},
        )
        return TokenResponse(access_token=token, user_id=user.id, organization_id=user.organization_id)
