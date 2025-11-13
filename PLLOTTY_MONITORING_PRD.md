# ploTTY Real-Time Monitoring System PRD

## Overview

This PRD defines a comprehensive real-time monitoring system for ploTTY, enabling users to track job progress, device status, and system performance through multiple interfaces including web dashboard, CLI monitoring, and programmatic APIs.

## Problem Statement

Currently, ploTTY users lack visibility into:
- Real-time job progress and estimated completion times
- Device status and connection health
- Historical performance and job patterns
- System-wide resource utilization
- Proactive error notifications and recovery suggestions

## Solution Architecture

### Core Components

#### 1. WebSocket Server (`plotty.websocket`)
- **Purpose**: Real-time bidirectional communication channel
- **Features**:
  - Job state streaming (queued, running, completed, failed)
  - Device status updates (connected, busy, error, offline)
  - Progress metrics with ETA calculations
  - System resource monitoring (CPU, memory, disk)
  - Authentication and session management

#### 2. Web Dashboard (`plotty.dashboard`)
- **Purpose**: Browser-based monitoring interface
- **Features**:
  - Real-time job queue visualization
  - Device status grid with health indicators
  - Interactive job timeline and Gantt charts
  - Performance analytics and historical trends
  - Alert management and configuration
  - Mobile-responsive design

#### 3. Notification System (`plotty.notifications`)
- **Purpose**: Multi-channel alerting and communication
- **Features**:
  - Email notifications for job completion/failures
  - Slack integration for team notifications
  - Webhook support for custom integrations
  - Configurable alert rules and thresholds
  - Notification templates and customization

#### 4. Enhanced CLI Monitor (`plotty.monitor`)
- **Purpose**: Terminal-based real-time monitoring
- **Features**:
  - Live progress bars with time estimates
  - Color-coded status indicators
  - Interactive job management (pause, resume, cancel)
  - Resource usage displays
  - Log streaming with filtering

#### 5. REST API (`plotty.api`)
- **Purpose**: Programmatic access to monitoring data
- **Features**:
  - Job status and history endpoints
  - Device management APIs
  - Performance metrics access
  - Alert configuration management
  - Authentication and rate limiting

## Technical Specifications

### Data Models

```python
# Enhanced Job Model
class JobStatus(Enum):
    QUEUED = "queued"
    RUNNING = "running" 
    PAUSED = "paused"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

class JobMetrics(BaseModel):
    progress_percentage: float
    estimated_time_remaining: Optional[int]
    current_layer: int
    total_layers: int
    points_plotted: int
    total_points: int
    pen_down_time: timedelta
    total_time: timedelta

class DeviceStatus(BaseModel):
    device_id: str
    connection_status: str
    current_job_id: Optional[str]
    last_heartbeat: datetime
    error_count: int
    uptime: timedelta
    firmware_version: str
```

### WebSocket Events

```python
# Client → Server
{
    "type": "subscribe",
    "channels": ["jobs", "devices", "alerts"]
}

{
    "type": "job_control",
    "job_id": "uuid",
    "action": "pause|resume|cancel"
}

# Server → Client
{
    "type": "job_update",
    "job_id": "uuid",
    "status": "running",
    "metrics": {...}
}

{
    "type": "device_alert",
    "device_id": "plotter_01",
    "severity": "warning",
    "message": "Low ink detected"
}
```

### API Endpoints

```
GET  /api/v1/jobs                    # List all jobs
GET  /api/v1/jobs/{job_id}           # Get job details
POST /api/v1/jobs/{job_id}/control   # Control job (pause/resume/cancel)
GET  /api/v1/devices                 # List all devices
GET  /api/v1/devices/{device_id}     # Get device status
GET  /api/v1/metrics                 # System metrics
GET  /api/v1/alerts                  # Alert history
POST /api/v1/alerts/rules            # Create alert rule
```

## Implementation Phases

### Phase 1: Core Infrastructure (Weeks 1-2)
- WebSocket server implementation
- Enhanced job state tracking
- Basic CLI monitor with real-time updates
- REST API foundation
- Unit tests and integration tests

### Phase 2: Web Dashboard (Weeks 3-4)
- React-based dashboard frontend
- Real-time data visualization
- Job queue management interface
- Device status monitoring
- Basic alerting system

### Phase 3: Notifications & Advanced Features (Weeks 5-6)
- Email notification system
- Slack integration
- Webhook support
- Advanced alert rules
- Performance analytics
- Historical data retention

### Phase 4: Polish & Documentation (Week 7-8)
- Mobile responsiveness
- Accessibility improvements
- Performance optimization
- Comprehensive documentation
- User guides and tutorials

## Configuration

### System Configuration (`~/.plotty/monitoring.yaml`)
```yaml
server:
  host: "localhost"
  port: 8765
  enable_auth: true

dashboard:
  enabled: true
  port: 8080
  refresh_interval: 1000  # ms

notifications:
  email:
    enabled: false
    smtp_server: "smtp.gmail.com"
    smtp_port: 587
    username: "user@example.com"
  
  slack:
    enabled: false
    webhook_url: "https://hooks.slack.com/..."
    channel: "#plotting"

alerts:
  job_failure:
    enabled: true
    channels: ["email", "slack"]
  
  device_offline:
    enabled: true
    threshold: 300  # seconds
    channels: ["email"]

retention:
  job_history: 90  # days
  metrics_data: 30  # days
  alert_history: 60  # days
```

## Security Considerations

- WebSocket authentication with JWT tokens
- API rate limiting and request validation
- Secure credential storage for notifications
- HTTPS support for web dashboard
- Role-based access control for enterprise deployments

## Performance Requirements

- Support 100+ concurrent WebSocket connections
- Sub-second latency for status updates
- Efficient memory usage for historical data
- Graceful degradation under high load
- Configurable data retention policies

## Testing Strategy

### Unit Tests
- WebSocket server functionality
- API endpoint validation
- Notification system testing
- Data model validation

### Integration Tests
- End-to-end job monitoring workflow
- Multi-device coordination
- Alert delivery verification
- Performance under load

### User Acceptance Tests
- Dashboard usability testing
- CLI monitor user experience
- Notification delivery reliability
- Mobile device compatibility

## Success Metrics

### Technical Metrics
- <100ms latency for status updates
- 99.9% WebSocket connection uptime
- Support for 50+ concurrent monitoring sessions
- <50MB memory footprint for monitoring service

### User Experience Metrics
- Reduced job status inquiry support tickets
- Improved plotting throughput through better visibility
- Faster error detection and recovery times
- High user satisfaction scores for dashboard usability

## Dependencies

### External Libraries
- `websockets` - WebSocket server implementation
- `fastapi` - REST API framework
- `react` + `typescript` - Dashboard frontend
- `redis` - Optional for session storage and caching
- `celery` - Optional for background task processing

### ploTTY Integration
- Enhanced `models.py` with monitoring fields
- Extended `fsm.py` with state change hooks
- Integration with existing job queue system
- Compatibility with current device management

## Migration Path

### For Existing Users
- Backward compatibility with current ploTTY versions
- Optional monitoring features (disabled by default)
- Gradual rollout with feature flags
- Migration guide for configuration updates

### For vpype-plotty Integration
- WebSocket connection endpoints for plugin monitoring
- Job status synchronization hooks
- Shared configuration management
- Unified alerting system

## Future Enhancements

### Advanced Analytics
- Machine learning for ETA prediction
- Anomaly detection for device failures
- Usage pattern analysis and optimization
- Predictive maintenance alerts

### Enterprise Features
- Multi-tenant support
- Advanced user roles and permissions
- Audit logging and compliance reporting
- Integration with enterprise monitoring systems

### Mobile Applications
- Native iOS/Android monitoring apps
- Push notifications for critical alerts
- Offline mode with cached data
- Voice control integration

## Conclusion

This real-time monitoring system will significantly enhance the ploTTY user experience by providing comprehensive visibility into plotting operations, proactive error detection, and flexible notification options. The modular architecture ensures easy integration with existing systems while providing a foundation for future enhancements.

The implementation will establish ploTTY as a professional-grade plotting solution with enterprise-ready monitoring capabilities, setting it apart from basic plotting tools and meeting the needs of both individual users and production environments.