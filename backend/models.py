"""Central model registry.

Alembic's env.py imports this module so that all table-mapped models are
registered on ``SQLModel.metadata`` before autogenerate runs.

Each model task (fn-2-szr.2 through fn-2-szr.4) adds its imports here.
"""

from backend.accounts.models import Account  # noqa: F401
from backend.calendars.models import Calendar  # noqa: F401
from backend.devices.models import Anchor, AnchorTagAssociation, Tag  # noqa: F401
from backend.notifications.models import NotificationPreference  # noqa: F401
