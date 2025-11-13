"""WebSocket message schemas for ploTTY integration compatibility."""

from __future__ import annotations

from enum import Enum
from typing import Dict, Any, List, Optional, Union, Literal
from datetime import datetime, timezone
from pydantic import BaseModel, Field


class Channel(str, Enum):
    """WebSocket event channels for subscription."""

    JOBS = "jobs"
    DEVICES = "devices"
    SYSTEM = "system"
    ALL = "all"


class MessageType(str, Enum):
    """WebSocket message types."""

    # Client -> Server
    SUBSCRIBE = "subscribe"
    UNSUBSCRIBE = "unsubscribe"
    PING = "ping"

    # Server -> Client
    JOB_STATE_CHANGE = "job_state_change"
    JOB_PROGRESS = "job_progress"
    DEVICE_STATUS = "device_status"
    SYSTEM_ALERT = "system_alert"
    PONG = "pong"
    ERROR = "error"


class BaseMessage(BaseModel):
    """Base WebSocket message structure."""

    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class SubscribeMessage(BaseMessage):
    """Subscribe to channels message."""

    type: Literal[MessageType.SUBSCRIBE]
    channels: List[Channel]


class UnsubscribeMessage(BaseMessage):
    """Unsubscribe from channels message."""

    type: Literal[MessageType.UNSUBSCRIBE]
    channels: List[Channel]


class PingMessage(BaseMessage):
    """Ping message for connection health check."""

    type: Literal[MessageType.PING]


class JobStateChangeMessage(BaseMessage):
    """Job state transition event."""

    type: Literal[MessageType.JOB_STATE_CHANGE]
    job_id: str
    from_state: Optional[str] = None
    to_state: str
    reason: str = ""
    metadata: Dict[str, Any] = Field(default_factory=dict)


class JobProgressMessage(BaseMessage):
    """Job progress update event."""

    type: Literal[MessageType.JOB_PROGRESS]
    job_id: str
    progress_percentage: float = Field(ge=0.0, le=100.0)
    current_layer: int = Field(ge=0)
    total_layers: int = Field(ge=0)
    points_plotted: int = Field(ge=0)
    total_points: int = Field(ge=0)
    eta_seconds: Optional[int] = None
    pen_down_time_seconds: float = Field(ge=0.0)
    total_time_seconds: float = Field(ge=0.0)


class DeviceStatusMessage(BaseMessage):
    """Device status update event."""

    type: Literal[MessageType.DEVICE_STATUS]
    device_id: str
    device_type: str = "axidraw"
    status: str  # connected, disconnected, busy, error, offline
    last_heartbeat: datetime
    error_count: int = Field(ge=0)
    uptime_seconds: Optional[float] = None
    firmware_version: Optional[str] = None
    current_job_id: Optional[str] = None
    error_message: Optional[str] = None


class SystemAlertMessage(BaseMessage):
    """System-level alert event."""

    type: Literal[MessageType.SYSTEM_ALERT]
    severity: str  # info, warning, error, critical
    title: str
    message: str
    source: str = "ploTTY"
    metadata: Dict[str, Any] = Field(default_factory=dict)


class ErrorMessage(BaseMessage):
    """Error message from server."""

    type: Literal[MessageType.ERROR]
    error_code: str
    error_message: str
    details: Optional[Dict[str, Any]] = None


class PongMessage(BaseMessage):
    """Pong response to client ping."""

    type: Literal[MessageType.PONG]


class VpypePlottyMessage(JobStateChangeMessage):
    """Extended message for vpype-plotty specific events."""

    source: str = "vpype-plotty"
    vpype_version: Optional[str] = None
    document_metadata: Optional[Dict[str, Any]] = None
    layer_count: Optional[int] = None
    total_distance: Optional[float] = None


# Union type for all server messages
ServerMessage = Union[
    JobStateChangeMessage,
    JobProgressMessage,
    DeviceStatusMessage,
    SystemAlertMessage,
    ErrorMessage,
    PongMessage,
]


# Channel subscription mappings
CHANNEL_EVENTS = {
    Channel.JOBS: [
        MessageType.JOB_STATE_CHANGE,
        MessageType.JOB_PROGRESS,
    ],
    Channel.DEVICES: [
        MessageType.DEVICE_STATUS,
    ],
    Channel.SYSTEM: [
        MessageType.SYSTEM_ALERT,
        MessageType.ERROR,
    ],
    Channel.ALL: [
        MessageType.JOB_STATE_CHANGE,
        MessageType.JOB_PROGRESS,
        MessageType.DEVICE_STATUS,
        MessageType.SYSTEM_ALERT,
        MessageType.ERROR,
    ],
}


def get_channels_for_message(message_type: MessageType) -> List[Channel]:
    """Get which channels a message type should be broadcast to."""
    channels = []
    for channel, event_types in CHANNEL_EVENTS.items():
        if message_type in event_types:
            channels.append(channel)
    return channels


def validate_message_channels(channels: List[Union[Channel, str]]) -> List[Channel]:
    """Validate and normalize channel list."""
    if not channels:
        return [Channel.ALL]

    # Remove duplicates and validate
    valid_channels = []
    for channel in set(channels):
        if isinstance(channel, Channel):
            valid_channels.append(channel)
        elif isinstance(channel, str):
            # Check if string matches any channel value
            for ch in Channel:
                if ch.value == channel:
                    valid_channels.append(ch)
                    break

    return valid_channels or [Channel.ALL]
