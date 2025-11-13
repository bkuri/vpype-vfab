"""Test WebSocket integration with ploTTY."""

import pytest
from unittest.mock import Mock, patch, AsyncMock
from datetime import datetime, timezone


class TestWebSocketIntegration:
    """Test WebSocket integration with ploTTY."""

    @pytest.fixture
    def mock_websocket_client(self):
        """Create a mock WebSocket client."""
        from vpype_plotty.websocket.client import PlottyWebSocketClient

        client = PlottyWebSocketClient()
        mock_connection = AsyncMock()

        # Mock the connect method directly
        async def mock_connect():
            client.websocket = mock_connection
            client.is_connected = True
            return True

        client.connect = mock_connect
        return client, mock_connection

    @pytest.mark.asyncio
    async def test_client_connection_success(self, mock_websocket_client):
        """Test successful WebSocket connection."""
        client, mock_connection = mock_websocket_client

        # Add error callback to capture errors
        errors = []

        def capture_error(error):
            errors.append(error)
            print(f"Debug - Captured error: {error}")

        client.add_error_callback(capture_error)

        # Test connection
        result = await client.connect()

        print(f"Debug - Connection result: {result}")
        print(f"Debug - Is connected: {client.is_connected}")
        print(f"Debug - WebSocket: {client.websocket}")
        print(f"Debug - Errors captured: {errors}")

        assert result is True
        assert client.is_connected is True
        assert client.websocket == mock_connection

    @pytest.mark.asyncio
    async def test_client_connection_failure(self):
        """Test WebSocket connection failure."""
        with patch("vpype_plotty.websocket.client.websockets") as mock_websockets:
            mock_websockets.connect.side_effect = OSError("Connection refused")

            from vpype_plotty.websocket.client import PlottyWebSocketClient

            client = PlottyWebSocketClient()

            # Test connection failure
            result = await client.connect()

            assert result is False
            assert client.is_connected is False

    @pytest.mark.asyncio
    async def test_subscribe_to_channels(self, mock_websocket_client):
        """Test subscribing to WebSocket channels."""
        client, mock_connection = mock_websocket_client

        # Connect first
        await client.connect()

        # Test subscription
        await client.subscribe(["jobs", "devices"])

        # Verify subscription message was sent
        mock_connection.send.assert_called_once()
        call_args = mock_connection.send.call_args[0][0]

        # Check that it's a valid subscription message
        import json

        message = json.loads(call_args)
        assert message["type"] == "subscribe"
        assert "jobs" in message["channels"]
        assert "devices" in message["channels"]

    @pytest.mark.asyncio
    async def test_message_parsing(self, mock_websocket_client):
        """Test parsing of WebSocket messages."""
        client, mock_connection = mock_websocket_client

        # Connect first
        await client.connect()

        # Mock message data
        test_message = {
            "type": "job_state_change",
            "job_id": "test-job-123",
            "from_state": "queued",
            "to_state": "running",
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

        # Test message parsing
        parsed_message = client._parse_message(test_message)

        assert parsed_message is not None
        assert parsed_message.job_id == "test-job-123"
        assert parsed_message.from_state == "queued"
        assert parsed_message.to_state == "running"

    @pytest.mark.asyncio
    async def test_connection_status(self, mock_websocket_client):
        """Test connection status reporting."""
        client, mock_connection = mock_websocket_client

        # Test disconnected status
        status = client.get_connection_status()
        assert status["connected"] is False
        assert status["host"] == "localhost"
        assert status["port"] == 8765

        # Connect and test connected status
        await client.connect()
        status = client.get_connection_status()
        assert status["connected"] is True
        assert "subscriptions" in status

    @pytest.mark.asyncio
    async def test_connection_test(self, mock_websocket_client):
        """Test connection testing functionality."""
        client, mock_connection = mock_websocket_client

        # Test successful connection test
        result = await client.test_connection()
        assert result is True

        # Verify disconnect was called
        mock_connection.close.assert_called_once()

    def test_error_callback_handling(self, mock_websocket_client):
        """Test error callback handling."""
        client, _ = mock_websocket_client

        # Add error callback
        error_callback = Mock()
        client.add_error_callback(error_callback)

        # Test error notification
        test_error = Exception("Test error")
        client._notify_error(test_error)

        # Verify callback was called
        error_callback.assert_called_once_with(test_error)

    def test_message_callback_handling(self, mock_websocket_client):
        """Test message callback handling."""
        client, _ = mock_websocket_client

        # Add message callback
        message_callback = Mock()
        client.add_message_callback(message_callback)

        # Test message notification
        from vpype_plotty.websocket.schemas import JobStateChangeMessage, MessageType

        test_message = JobStateChangeMessage(
            type=MessageType.JOB_STATE_CHANGE,
            job_id="test-job",
            from_state="queued",
            to_state="running",
        )

        client._notify_message(test_message)

        # Verify callback was called
        message_callback.assert_called_once_with(test_message)

    @pytest.mark.asyncio
    async def test_graceful_disconnect(self, mock_websocket_client):
        """Test graceful WebSocket disconnection."""
        client, mock_connection = mock_websocket_client

        # Connect first
        await client.connect()
        assert client.is_connected is True

        # Test disconnect
        await client.disconnect()

        assert client.is_connected is False
        assert client.websocket is None
        mock_connection.close.assert_called_once()


class TestWebSocketSchemas:
    """Test WebSocket message schemas."""

    def test_job_state_change_message(self):
        """Test JobStateChangeMessage schema."""
        from vpype_plotty.websocket.schemas import JobStateChangeMessage, MessageType

        message = JobStateChangeMessage(
            type=MessageType.JOB_STATE_CHANGE,
            job_id="test-job-123",
            from_state="queued",
            to_state="running",
            reason="Started by user",
        )

        assert message.type == MessageType.JOB_STATE_CHANGE
        assert message.job_id == "test-job-123"
        assert message.from_state == "queued"
        assert message.to_state == "running"
        assert message.reason == "Started by user"
        assert isinstance(message.timestamp, datetime)

    def test_job_progress_message(self):
        """Test JobProgressMessage schema."""
        from vpype_plotty.websocket.schemas import JobProgressMessage, MessageType

        message = JobProgressMessage(
            type=MessageType.JOB_PROGRESS,
            job_id="test-job-123",
            progress_percentage=45.5,
            current_layer=2,
            total_layers=5,
            points_plotted=1000,
            total_points=2200,
            eta_seconds=120,
            pen_down_time_seconds=60.0,
            total_time_seconds=120.0,
        )

        assert message.type == MessageType.JOB_PROGRESS
        assert message.job_id == "test-job-123"
        assert message.progress_percentage == 45.5
        assert message.current_layer == 2
        assert message.total_layers == 5
        assert message.points_plotted == 1000
        assert message.total_points == 2200
        assert message.eta_seconds == 120
        assert message.pen_down_time_seconds == 60.0
        assert message.total_time_seconds == 120.0

    def test_device_status_message(self):
        """Test DeviceStatusMessage schema."""
        from vpype_plotty.websocket.schemas import DeviceStatusMessage, MessageType
        from datetime import datetime, timezone

        message = DeviceStatusMessage(
            type=MessageType.DEVICE_STATUS,
            device_id="axidraw-001",
            device_type="axidraw",
            status="connected",
            last_heartbeat=datetime.now(timezone.utc),
            error_count=0,
            firmware_version="v2.5.0",
        )

        assert message.type == MessageType.DEVICE_STATUS
        assert message.device_id == "axidraw-001"
        assert message.device_type == "axidraw"
        assert message.status == "connected"
        assert message.error_count == 0
        assert message.firmware_version == "v2.5.0"

    def test_system_alert_message(self):
        """Test SystemAlertMessage schema."""
        from vpype_plotty.websocket.schemas import SystemAlertMessage, MessageType

        message = SystemAlertMessage(
            type=MessageType.SYSTEM_ALERT,
            severity="warning",
            title="Low Ink",
            message="Pen 1 running low on ink",
            source="axidraw-001",
        )

        assert message.type == MessageType.SYSTEM_ALERT
        assert message.severity == "warning"
        assert message.title == "Low Ink"
        assert message.message == "Pen 1 running low on ink"
        assert message.source == "axidraw-001"

    def test_vpype_plotty_message(self):
        """Test VpypePlottyMessage extended schema."""
        from vpype_plotty.websocket.schemas import VpypePlottyMessage, MessageType

        message = VpypePlottyMessage(
            type=MessageType.JOB_STATE_CHANGE,
            job_id="test-job-123",
            from_state="new",
            to_state="queued",
            source="vpype-plotty",
            vpype_version="1.14.0",
            layer_count=3,
            total_distance=1500.5,
        )

        assert message.type == MessageType.JOB_STATE_CHANGE
        assert message.job_id == "test-job-123"
        assert message.source == "vpype-plotty"
        assert message.vpype_version == "1.14.0"
        assert message.layer_count == 3
        assert message.total_distance == 1500.5

    def test_channel_validation(self):
        """Test channel validation."""
        from vpype_plotty.websocket.schemas import validate_message_channels, Channel

        # Test valid channels
        channels = validate_message_channels(["jobs", "devices"])
        print(f"Debug - channels returned: {channels}")
        assert Channel.JOBS in channels
        assert Channel.DEVICES in channels

        # Test empty channels (should default to ALL)
        channels = validate_message_channels([])
        assert Channel.ALL in channels

        # Test invalid channels (should be filtered out)
        channels = validate_message_channels(["invalid", "jobs"])
        assert Channel.JOBS in channels
        assert len(channels) == 1  # only jobs (invalid filtered out)

    def test_channel_routing(self):
        """Test message to channel routing."""
        from vpype_plotty.websocket.schemas import (
            get_channels_for_message,
            MessageType,
            Channel,
        )

        # Test job state change routing
        channels = get_channels_for_message(MessageType.JOB_STATE_CHANGE)
        assert Channel.JOBS in channels
        assert Channel.ALL in channels

        # Test device status routing
        channels = get_channels_for_message(MessageType.DEVICE_STATUS)
        assert Channel.DEVICES in channels
        assert Channel.ALL in channels

        # Test system alert routing
        channels = get_channels_for_message(MessageType.SYSTEM_ALERT)
        assert Channel.SYSTEM in channels
        assert Channel.ALL in channels
