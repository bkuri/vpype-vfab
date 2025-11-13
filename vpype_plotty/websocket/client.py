"""WebSocket client for ploTTY real-time monitoring."""

from __future__ import annotations

import json
import logging
from typing import Dict, Any, List, Optional, Callable, Set
from datetime import datetime, timezone

import websockets
from websockets.exceptions import ConnectionClosed

from vpype_plotty.websocket.schemas import (
    Channel,
    MessageType,
    SubscribeMessage,
    UnsubscribeMessage,
    PingMessage,
    ServerMessage,
    validate_message_channels,
)

logger = logging.getLogger(__name__)


class WebSocketConnectionError(Exception):
    """Raised when WebSocket connection to ploTTY fails."""

    pass


class WebSocketSubscriptionError(Exception):
    """Raised when WebSocket subscription fails."""

    pass


class PlottyWebSocketClient:
    """WebSocket client for ploTTY real-time monitoring."""

    def __init__(self, host: str = "localhost", port: int = 8765):
        """Initialize WebSocket client.

        Args:
            host: ploTTY WebSocket server host
            port: ploTTY WebSocket server port
        """
        self.host = host
        self.port = port
        self.websocket: Optional[websockets.ClientConnection] = None
        self.subscriptions: Set[Channel] = set()
        self.is_connected = False
        self.connection_url = f"ws://{host}:{port}/ws"
        self._message_callbacks: List[Callable[[ServerMessage], None]] = []
        self._error_callbacks: List[Callable[[Exception], None]] = []

    def add_message_callback(self, callback: Callable[[ServerMessage], None]) -> None:
        """Add callback for received messages."""
        self._message_callbacks.append(callback)

    def add_error_callback(self, callback: Callable[[Exception], None]) -> None:
        """Add callback for connection errors."""
        self._error_callbacks.append(callback)

    async def connect(self) -> bool:
        """Connect to ploTTY WebSocket server.

        Returns:
            True if connection successful, False otherwise
        """
        try:
            logger.info(f"Connecting to ploTTY WebSocket at {self.connection_url}")
            self.websocket = await websockets.connect(
                self.connection_url,
                ping_interval=30,
                ping_timeout=10,
                close_timeout=10,
            )
            self.is_connected = True
            logger.info("Successfully connected to ploTTY WebSocket")
            return True

        except OSError as e:
            if "Connection refused" in str(e):
                error = WebSocketConnectionError(
                    f"Connection refused. Is ploTTY running at {self.connection_url}?"
                )
            else:
                error = WebSocketConnectionError(f"Failed to connect to ploTTY: {e}")
            self._notify_error(error)
            return False

        except Exception as e:
            error = WebSocketConnectionError(f"Failed to connect to ploTTY: {e}")
            self._notify_error(error)
            return False

    async def disconnect(self) -> None:
        """Disconnect from ploTTY WebSocket server."""
        if self.websocket:
            try:
                await self.websocket.close()
            except Exception:
                pass  # Ignore errors during close
            finally:
                self.websocket = None
                self.is_connected = False
                logger.info("Disconnected from ploTTY WebSocket")

    async def subscribe(self, channels: List[str]) -> None:
        """Subscribe to ploTTY channels.

        Args:
            channels: List of channel names to subscribe to

        Raises:
            WebSocketSubscriptionError: If subscription fails
        """
        if not self.is_connected or not self.websocket:
            raise WebSocketSubscriptionError("Not connected to ploTTY WebSocket")

        try:
            # Validate and normalize channels
            validated_channels = validate_message_channels(
                [Channel(ch) for ch in channels]
            )
            self.subscriptions.update(validated_channels)

            # Send subscription message
            subscribe_msg = SubscribeMessage(
                type=MessageType.SUBSCRIBE,
                channels=list(validated_channels),
            )
            await self.websocket.send(subscribe_msg.model_dump_json())
            logger.info(
                f"Subscribed to channels: {[ch.value for ch in validated_channels]}"
            )

        except Exception as e:
            raise WebSocketSubscriptionError(f"Failed to subscribe to channels: {e}")

    async def unsubscribe(self, channels: List[str]) -> None:
        """Unsubscribe from ploTTY channels.

        Args:
            channels: List of channel names to unsubscribe from
        """
        if not self.is_connected or not self.websocket:
            return  # Not connected, nothing to unsubscribe

        try:
            # Validate channels
            validated_channels = validate_message_channels(
                [Channel(ch) for ch in channels]
            )
            self.subscriptions.difference_update(validated_channels)

            # Send unsubscription message
            unsubscribe_msg = UnsubscribeMessage(
                type=MessageType.UNSUBSCRIBE,
                channels=list(validated_channels),
            )
            await self.websocket.send(unsubscribe_msg.model_dump_json())
            logger.info(
                f"Unsubscribed from channels: {[ch.value for ch in validated_channels]}"
            )

        except Exception as e:
            logger.warning(f"Failed to unsubscribe from channels: {e}")

    async def ping(self) -> None:
        """Send ping message to server."""
        if not self.is_connected or not self.websocket:
            return

        try:
            ping_msg = PingMessage(type=MessageType.PING)
            await self.websocket.send(ping_msg.model_dump_json())
        except Exception as e:
            logger.warning(f"Failed to send ping: {e}")

    async def listen(self) -> None:
        """Listen for ploTTY messages and call callbacks.

        This method runs indefinitely until disconnected or an error occurs.
        """
        if not self.is_connected or not self.websocket:
            raise WebSocketConnectionError("Not connected to ploTTY WebSocket")

        logger.info("Starting to listen for ploTTY messages")

        try:
            async for message in self.websocket:
                try:
                    # Parse message
                    message_data = json.loads(message)
                    server_message = self._parse_message(message_data)

                    if server_message:
                        self._notify_message(server_message)

                except json.JSONDecodeError as e:
                    logger.warning(f"Received invalid JSON: {e}")
                except Exception as e:
                    logger.warning(f"Error processing message: {e}")

        except ConnectionClosed:
            logger.info("ploTTY WebSocket connection closed")
            self.is_connected = False
        except Exception as e:
            error = WebSocketConnectionError(f"WebSocket error: {e}")
            self._notify_error(error)
            self.is_connected = False

    def _parse_message(self, message_data: Dict[str, Any]) -> Optional[ServerMessage]:
        """Parse incoming message data into appropriate message type.

        Args:
            message_data: Raw message data from WebSocket

        Returns:
            Parsed ServerMessage or None if parsing failed
        """
        try:
            message_type = message_data.get("type")

            # Add timestamp if not present
            if "timestamp" not in message_data:
                message_data["timestamp"] = datetime.now(timezone.utc).isoformat()

            # Parse based on message type
            if message_type == MessageType.JOB_STATE_CHANGE.value:
                from vpype_plotty.websocket.schemas import JobStateChangeMessage

                return JobStateChangeMessage(**message_data)
            elif message_type == MessageType.JOB_PROGRESS.value:
                from vpype_plotty.websocket.schemas import JobProgressMessage

                return JobProgressMessage(**message_data)
            elif message_type == MessageType.DEVICE_STATUS.value:
                from vpype_plotty.websocket.schemas import DeviceStatusMessage

                return DeviceStatusMessage(**message_data)
            elif message_type == MessageType.SYSTEM_ALERT.value:
                from vpype_plotty.websocket.schemas import SystemAlertMessage

                return SystemAlertMessage(**message_data)
            elif message_type == MessageType.PONG.value:
                from vpype_plotty.websocket.schemas import PongMessage

                return PongMessage(**message_data)
            elif message_type == MessageType.ERROR.value:
                from vpype_plotty.websocket.schemas import ErrorMessage

                return ErrorMessage(**message_data)
            else:
                logger.warning(f"Unknown message type: {message_type}")
                return None

        except Exception as e:
            logger.warning(f"Failed to parse message: {e}")
            return None

    def _notify_message(self, message: ServerMessage) -> None:
        """Notify all message callbacks."""
        for callback in self._message_callbacks:
            try:
                callback(message)
            except Exception as e:
                logger.warning(f"Message callback error: {e}")

    def _notify_error(self, error: Exception) -> None:
        """Notify all error callbacks."""
        for callback in self._error_callbacks:
            try:
                callback(error)
            except Exception as e:
                logger.warning(f"Error callback error: {e}")

    def get_connection_status(self) -> Dict[str, Any]:
        """Get current connection status.

        Returns:
            Dictionary with connection status information
        """
        return {
            "connected": self.is_connected,
            "url": self.connection_url,
            "subscriptions": [ch.value for ch in self.subscriptions],
            "host": self.host,
            "port": self.port,
        }

    async def test_connection(self) -> bool:
        """Test WebSocket connection to ploTTY.

        Returns:
            True if connection test successful, False otherwise
        """
        try:
            # Try to connect and immediately disconnect
            if await self.connect():
                await self.disconnect()
                return True
            return False
        except Exception:
            return False
