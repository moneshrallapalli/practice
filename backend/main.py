"""
Main FastAPI application for SentinTinel Surveillance System
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager
import asyncio
import uvicorn
from loguru import logger

from config import settings
from database import init_db
from api import router, ws_router
from services import camera_service


# Startup and shutdown events
@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan context manager for startup and shutdown
    """
    # Startup
    logger.info("Starting SentinTinel Surveillance System...")

    # Initialize database
    init_db()
    logger.info("Database initialized")

    # Start background tasks
    asyncio.create_task(surveillance_worker())
    logger.info("Surveillance worker started")

    yield

    # Shutdown
    logger.info("Shutting down...")
    await camera_service.stop_all_cameras()
    logger.info("All cameras stopped")


# Create FastAPI app
app = FastAPI(
    title="SentinTinel Surveillance API",
    description="AI-powered surveillance system with Gemini integration",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(router, prefix="/api", tags=["api"])
app.include_router(ws_router, tags=["websocket"])


# Root endpoint
@app.get("/")
async def root():
    """
    Root endpoint
    """
    return {
        "name": "SentinTinel Surveillance System",
        "version": "1.0.0",
        "status": "running",
        "docs": "/docs"
    }


@app.get("/health")
async def health():
    """
    Health check endpoint
    """
    return {"status": "healthy"}


# Background worker for surveillance processing
async def surveillance_worker():
    """
    Background worker that processes camera feeds
    """
    from agents import VisionAgent, ContextAgent, CommandAgent
    from api import manager
    from database import SessionLocal, Event, Detection, Alert, AlertSeverity
    from datetime import datetime
    import base64
    import cv2

    vision_agent = VisionAgent()
    context_agent = ContextAgent()
    command_agent = CommandAgent()

    logger.info("Surveillance worker started")

    while True:
        try:
            # Get active cameras
            active_camera_count = camera_service.get_active_camera_count()

            if active_camera_count > 0:
                # Process each active camera
                for camera_id in list(camera_service.active_cameras.keys()):
                    # Capture frame
                    frame = await camera_service.capture_frame(camera_id)

                    if frame is not None:
                        # Analyze frame with Vision Agent
                        analysis = await vision_agent.analyze_frame(frame, camera_id)

                        # Get context from Context Agent
                        context_summary = await context_agent.get_context_for_event(
                            analysis.get('scene_description', ''),
                            datetime.utcnow(),
                            camera_id
                        )

                        # Store event in database
                        db = SessionLocal()
                        try:
                            # Create event
                            event = Event(
                                camera_id=camera_id,
                                event_type="scene_analysis",
                                description=analysis.get('activity', ''),
                                scene_description=analysis.get('scene_description', ''),
                                significance_score=vision_agent.calculate_significance_score(analysis),
                                severity=vision_agent.determine_alert_severity(analysis),
                                context_summary=context_summary,
                                event_metadata=analysis
                            )

                            db.add(event)
                            db.flush()  # Get event ID

                            # Store in ChromaDB
                            embedding_id = await context_agent.store_scene_description(
                                event.id,
                                camera_id,
                                event.timestamp,
                                event.scene_description,
                                {"significance": event.significance_score}
                            )

                            event.embedding_id = embedding_id

                            # Create detections
                            for det in vision_agent.extract_detections_for_storage(analysis):
                                detection = Detection(
                                    event_id=event.id,
                                    camera_id=camera_id,
                                    **det
                                )
                                db.add(detection)

                            # Create alert if significant
                            if event.significance_score >= settings.WARNING_THRESHOLD:
                                alert = Alert(
                                    event_id=event.id,
                                    severity=event.severity,
                                    title=f"{event.severity.value} Alert - Camera {camera_id}",
                                    message=event.scene_description
                                )
                                db.add(alert)
                                db.flush()

                                # Send alert via WebSocket
                                await manager.send_alert({
                                    "id": alert.id,
                                    "severity": alert.severity.value,
                                    "title": alert.title,
                                    "message": alert.message,
                                    "camera_id": camera_id,
                                    "timestamp": alert.timestamp.isoformat()
                                })

                            db.commit()

                            # Send live feed update via WebSocket
                            _, buffer = cv2.imencode('.jpg', frame)
                            frame_base64 = base64.b64encode(buffer).decode('utf-8')

                            await manager.send_live_feed_update(
                                camera_id,
                                frame_base64,
                                analysis
                            )

                            # Send analysis update
                            await manager.send_analysis_update({
                                "camera_id": camera_id,
                                "scene_description": analysis.get('scene_description', ''),
                                "significance": event.significance_score,
                                "detections": len(analysis.get('detections', [])),
                                "context": context_summary
                            })

                            # Check active tasks and analyze in context
                            active_tasks = command_agent.get_active_tasks()
                            for task_id, task_data in active_tasks.items():
                                task_command = task_data.get('command', {})
                                task_params = task_command.get('parameters', {})
                                target_cameras = task_params.get('camera_ids', ['all'])

                                # Check if this camera is relevant to the task
                                if target_cameras == ['all'] or 'all' in target_cameras or camera_id in target_cameras:
                                    # Analyze in context of task
                                    task_result = await command_agent.analyze_with_context(
                                        task_id,
                                        {"camera_id": camera_id, "timestamp": datetime.utcnow().isoformat()},
                                        analysis
                                    )

                                    # Send task update if alert needed
                                    if task_result.get('alert_needed'):
                                        await manager.send_system_message("task_alert", {
                                            "task_id": task_id,
                                            "camera_id": camera_id,
                                            "task_type": task_command.get('task_type'),
                                            "target": task_command.get('target'),
                                            "findings": task_result.get('findings'),
                                            "alert_message": task_result.get('alert_message'),
                                            "timestamp": datetime.utcnow().isoformat()
                                        })

                                        # Also create an alert
                                        task_alert = Alert(
                                            event_id=event.id,
                                            severity=AlertSeverity.WARNING,
                                            title=f"Task Alert: {task_command.get('target', 'Unknown')}",
                                            message=task_result.get('alert_message', 'Task condition met')
                                        )
                                        db.add(task_alert)
                                        db.commit()

                        except Exception as e:
                            db.rollback()
                            logger.error(f"Error storing event: {e}")
                        finally:
                            db.close()

            # Wait before next iteration (based on FPS)
            await asyncio.sleep(1.0 / settings.CAMERA_FPS)

        except Exception as e:
            logger.error(f"Error in surveillance worker: {e}")
            await asyncio.sleep(1)


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=settings.APP_HOST,
        port=settings.APP_PORT,
        reload=settings.DEBUG,
        log_level=settings.LOG_LEVEL.lower()
    )
