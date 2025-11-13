"""WebSocket integration for ploTTY real-time monitoring."""

from vpype_plotty.websocket.client import (
    PlottyWebSocketClient,
    WebSocketConnectionError,
    WebSocketSubscriptionError,
)
from vpype_plotty.websocket.schemas import VpypePlottyMessage

__all__ = [
    "PlottyWebSocketClient",
    "VpypePlottyMessage",
    "WebSocketConnectionError",
    "WebSocketSubscriptionError",
]
