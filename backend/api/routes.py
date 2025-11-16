"""
API routes for SentinTinel Surveillance System
"""
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, timedelta
import base64
import cv2
import numpy as np
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import get_db, Camera, Event, Detection, Alert, ContextPattern, AlertSeverity
from api.websocket import manager
from agents import VisionAgent, ContextAgent, CommandAgent
from services import camera_service
from config import settings

# Create routers
router = APIRouter()
ws_router = APIRouter()

# Initialize agents
vision_agent = VisionAgent()
context_agent = ContextAgent()
command_agent = CommandAgent()


# WebSocket endpoints
@ws_router.websocket("/ws/live-feed")
async def websocket_live_feed(websocket: WebSocket):
    """
    WebSocket endpoint for live video feed and analysis
    """
    await manager.connect(websocket, "live_feed")

    try:
        while True:
            # Receive messages from client (e.g., camera selection)
            data = await websocket.receive_json()

            # Handle client requests
            if data.get("action") == "start_camera":
                camera_id = data.get("camera_id")
                # Client will receive updates via broadcast

            elif data.get("action") == "stop_camera":
                camera_id = data.get("camera_id")
                # Handle camera stop

    except WebSocketDisconnect:
        manager.disconnect(websocket)


@ws_router.websocket("/ws/alerts")
async def websocket_alerts(websocket: WebSocket):
    """
    WebSocket endpoint for real-time alerts
    """
    await manager.connect(websocket, "alerts")

    try:
        while True:
            await websocket.receive_text()  # Keep connection alive
    except WebSocketDisconnect:
        manager.disconnect(websocket)


@ws_router.websocket("/ws/analysis")
async def websocket_analysis(websocket: WebSocket):
    """
    WebSocket endpoint for scene analysis/narration
    """
    await manager.connect(websocket, "analysis")

    try:
        while True:
            await websocket.receive_text()  # Keep connection alive
    except WebSocketDisconnect:
        manager.disconnect(websocket)


@ws_router.websocket("/ws/system")
async def websocket_system(websocket: WebSocket):
    """
    WebSocket endpoint for system messages and commands
    """
    await manager.connect(websocket, "system")

    try:
        while True:
            data = await websocket.receive_json()

            # Handle system commands
            if data.get("command"):
                await handle_system_command(data["command"], data.get("params", {}))

    except WebSocketDisconnect:
        manager.disconnect(websocket)


# REST API endpoints
@router.get("/cameras")
async def get_cameras(db: Session = Depends(get_db)):
    """
    Get all cameras
    """
    cameras = db.query(Camera).all()
    return cameras


@router.post("/cameras")
async def create_camera(
    name: str,
    location: str,
    stream_url: str,
    db: Session = Depends(get_db)
):
    """
    Create a new camera
    """
    camera = Camera(
        name=name,
        location=location,
        stream_url=stream_url,
        is_active=True
    )

    db.add(camera)
    db.commit()
    db.refresh(camera)

    return camera


@router.post("/cameras/{camera_id}/start")
async def start_camera(camera_id: int, db: Session = Depends(get_db)):
    """
    Start a camera feed
    """
    camera = db.query(Camera).filter(Camera.id == camera_id).first()

    if not camera:
        raise HTTPException(status_code=404, detail="Camera not found")

    # Initialize camera
    success = await camera_service.initialize_camera(
        camera_id,
        camera.stream_url or camera_id,  # Use stream_url or camera index
        fps=camera.fps
    )

    if success:
        camera.is_active = True
        db.commit()
        return {"status": "started", "camera_id": camera_id}
    else:
        raise HTTPException(status_code=500, detail="Failed to start camera")


@router.post("/cameras/{camera_id}/stop")
async def stop_camera(camera_id: int, db: Session = Depends(get_db)):
    """
    Stop a camera feed
    """
    camera = db.query(Camera).filter(Camera.id == camera_id).first()

    if not camera:
        raise HTTPException(status_code=404, detail="Camera not found")

    await camera_service.stop_camera(camera_id)
    camera.is_active = False
    db.commit()

    return {"status": "stopped", "camera_id": camera_id}


@router.get("/events")
async def get_events(
    camera_id: Optional[int] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    severity: Optional[AlertSeverity] = None,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """
    Get events with filtering
    """
    query = db.query(Event)

    if camera_id:
        query = query.filter(Event.camera_id == camera_id)
    if start_date:
        query = query.filter(Event.timestamp >= start_date)
    if end_date:
        query = query.filter(Event.timestamp <= end_date)
    if severity:
        query = query.filter(Event.severity == severity)

    events = query.order_by(Event.timestamp.desc()).limit(limit).all()
    return events


@router.get("/alerts")
async def get_alerts(
    is_read: Optional[bool] = None,
    severity: Optional[AlertSeverity] = None,
    limit: int = 50,
    db: Session = Depends(get_db)
):
    """
    Get alerts with filtering
    """
    query = db.query(Alert)

    if is_read is not None:
        query = query.filter(Alert.is_read == is_read)
    if severity:
        query = query.filter(Alert.severity == severity)

    alerts = query.order_by(Alert.timestamp.desc()).limit(limit).all()
    return alerts


@router.post("/alerts/{alert_id}/acknowledge")
async def acknowledge_alert(alert_id: int, db: Session = Depends(get_db)):
    """
    Acknowledge an alert
    """
    alert = db.query(Alert).filter(Alert.id == alert_id).first()

    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")

    alert.is_read = True
    alert.acknowledged_at = datetime.utcnow()

    if alert.event:
        response_time = (alert.acknowledged_at - alert.event.timestamp).total_seconds()
        alert.response_time_seconds = int(response_time)

    db.commit()

    return alert


@router.get("/stats/summary")
async def get_summary_stats(
    hours: int = 24,
    db: Session = Depends(get_db)
):
    """
    Get summary statistics
    """
    since = datetime.utcnow() - timedelta(hours=hours)

    total_events = db.query(Event).filter(Event.timestamp >= since).count()
    critical_alerts = db.query(Alert).filter(
        Alert.timestamp >= since,
        Alert.severity == AlertSeverity.CRITICAL
    ).count()
    warning_alerts = db.query(Alert).filter(
        Alert.timestamp >= since,
        Alert.severity == AlertSeverity.WARNING
    ).count()

    # Average response time
    acknowledged_alerts = db.query(Alert).filter(
        Alert.timestamp >= since,
        Alert.acknowledged_at.isnot(None)
    ).all()

    avg_response_time = 0
    if acknowledged_alerts:
        total_response = sum(a.response_time_seconds for a in acknowledged_alerts if a.response_time_seconds)
        avg_response_time = total_response / len(acknowledged_alerts) if acknowledged_alerts else 0

    # Get ChromaDB stats
    chroma_stats = context_agent.get_statistics()

    return {
        "period_hours": hours,
        "total_events": total_events,
        "critical_alerts": critical_alerts,
        "warning_alerts": warning_alerts,
        "info_alerts": total_events - critical_alerts - warning_alerts,
        "avg_response_time_seconds": int(avg_response_time),
        "active_cameras": camera_service.get_active_camera_count(),
        "context_stats": chroma_stats
    }


@router.get("/patterns")
async def get_patterns(
    camera_id: Optional[int] = None,
    db: Session = Depends(get_db)
):
    """
    Get identified patterns
    """
    query = db.query(ContextPattern).filter(ContextPattern.is_active == True)

    patterns_db = query.order_by(ContextPattern.frequency.desc()).limit(20).all()

    # Also get patterns from context agent
    patterns_chroma = await context_agent.identify_patterns(camera_id=camera_id)

    return {
        "database_patterns": patterns_db,
        "detected_patterns": patterns_chroma
    }


@router.get("/system/health")
async def health_check():
    """
    System health check
    """
    connection_stats = manager.get_connection_stats()

    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "websocket_connections": connection_stats,
        "active_cameras": camera_service.get_active_camera_count(),
        "version": "1.0.0"
    }


# Helper functions
async def handle_system_command(command: str, params: dict):
    """
    Handle system commands from WebSocket
    """
    if command == "get_stats":
        stats = manager.get_connection_stats()
        await manager.send_system_message("stats_response", stats)

    elif command == "test_alert":
        await manager.send_alert({
            "severity": "INFO",
            "title": "Test Alert",
            "message": "This is a test alert",
            "camera_id": params.get("camera_id", 1)
        })

    else:
        # Process as natural language command with Gemini
        await process_user_command(command, params)


async def process_user_command(command: str, params: dict):
    """
    Process natural language user command with Gemini

    Args:
        command: User's natural language command
        params: Additional parameters
    """
    try:
        # Get current context
        active_camera_ids = list(camera_service.active_cameras.keys())
        context = {
            "active_cameras": active_camera_ids,
            "timestamp": datetime.utcnow().isoformat()
        }

        # Process command with CommandAgent
        result = await command_agent.process_command(command, context)

        # Send confirmation to user
        await manager.send_system_message("command_processed", {
            "original_command": command,
            "task_id": result.get('task_id'),
            "task_type": result.get('task_type'),
            "confirmation": result.get('confirmation'),
            "understood_intent": result.get('understood_intent'),
            "parameters": result.get('parameters')
        })

        # Execute task based on type
        task_type = result.get('task_type')

        if task_type in ['object_detection', 'surveillance', 'scene_analysis', 'anomaly_detection', 'tracking']:
            # Start monitoring task
            await start_monitoring_task(result)

        elif task_type == 'alert':
            # Create immediate alert
            await manager.send_alert({
                "severity": "INFO",
                "title": "Command Alert",
                "message": result.get('confirmation'),
                "camera_id": params.get("camera_id", 1)
            })

    except Exception as e:
        await manager.send_system_message("command_error", {
            "error": str(e),
            "message": f"Failed to process command: {str(e)}"
        })


async def start_monitoring_task(task_command: dict):
    """
    Start a monitoring task based on parsed command

    Args:
        task_command: Parsed command from CommandAgent
    """
    task_id = task_command.get('task_id')
    camera_ids = task_command.get('parameters', {}).get('camera_ids', ['all'])

    # Determine which cameras to monitor
    if camera_ids == ['all'] or 'all' in camera_ids:
        target_cameras = list(camera_service.active_cameras.keys())
    else:
        target_cameras = [int(cid) for cid in camera_ids if isinstance(cid, (int, str))]

    # Send status update
    await manager.send_system_message("task_started", {
        "task_id": task_id,
        "task_type": task_command.get('task_type'),
        "target": task_command.get('target'),
        "cameras": target_cameras,
        "message": f"Started monitoring on {len(target_cameras)} camera(s)"
    })
