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

    # Initialize database (optional - continue if fails)
    try:
        init_db()
        logger.info("Database initialized")
    except Exception as e:
        logger.warning(f"Database initialization failed (continuing without database): {e}")
        logger.info("Some features requiring database access will not be available")

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

# Mount event frames directory for static file access
from pathlib import Path
event_frames_path = Path(__file__).parent / "event_frames"
event_frames_path.mkdir(exist_ok=True)
app.mount("/event_frames", StaticFiles(directory=str(event_frames_path)), name="event_frames")


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
    Background worker with 1-minute analysis intervals to reduce noise
    """
    from agents import VisionAgent, ContextAgent, CommandAgent
    from api import manager
    from database import SessionLocal, Event, Detection, Alert, AlertSeverity
    from datetime import datetime, timedelta
    import base64
    import cv2
    import os
    from pathlib import Path

    vision_agent = VisionAgent()
    context_agent = ContextAgent()
    command_agent = CommandAgent()

    # Create event frames directory
    event_frames_dir = Path(__file__).parent / "event_frames"
    event_frames_dir.mkdir(exist_ok=True)

    logger.info("🎯 Surveillance worker started with 2-MINUTE summaries (immediate alerts >=60%)")

    # 2-minute aggregation state
    ANALYSIS_INTERVAL_SECONDS = 120  # 2 minutes for summary
    minute_start_time = datetime.utcnow()
    critical_events = []  # Store events for 2-min summary (non-immediate alerts)

    iteration = 0
    while True:
        try:
            iteration += 1
            current_time = datetime.utcnow()
            elapsed_seconds = (current_time - minute_start_time).total_seconds()
            
            logger.info(f"[WORKER] Iteration {iteration} - Elapsed: {int(elapsed_seconds)}s/{ANALYSIS_INTERVAL_SECONDS}s, Critical events: {len(critical_events)}")

            # Get active cameras
            active_camera_count = camera_service.get_active_camera_count()
            logger.debug(f"[WORKER] Active camera count: {active_camera_count}")

            if active_camera_count > 0:
                logger.info(f"Processing {active_camera_count} active camera(s)")
                # Process each active camera
                for camera_id in list(camera_service.active_cameras.keys()):
                    # Capture frame
                    frame = await camera_service.capture_frame(camera_id)

                    if frame is None:
                        logger.debug(f"No frame captured from camera {camera_id}")
                        continue

                    if frame is not None:
                        logger.info(f"Processing frame from camera {camera_id}, shape: {frame.shape}")
                        try:
                            # Analyze frame with Vision Agent
                            analysis = await vision_agent.analyze_frame(frame, camera_id)
                            logger.info(f"[ANALYSIS] Camera {camera_id} - Scene: {analysis.get('scene_description', 'N/A')[:100]}, Error: {analysis.get('error', 'None')}")

                            # Get context from Context Agent
                            context_summary = await context_agent.get_context_for_event(
                                analysis.get('scene_description', ''),
                                datetime.utcnow(),
                                camera_id
                            )

                            # Send live feed update via WebSocket (works without database)
                            _, buffer = cv2.imencode('.jpg', frame)
                            frame_base64 = base64.b64encode(buffer).decode('utf-8')

                            await manager.send_live_feed_update(
                                camera_id,
                                frame_base64,
                                analysis
                            )

                            # Calculate significance
                            significance = vision_agent.calculate_significance_score(analysis)

                            # Save EVERY frame with timestamp for quick access
                            timestamp_str = datetime.utcnow().strftime("%Y%m%d_%H%M%S_%f")
                            frame_filename = f"camera{camera_id}_{timestamp_str}.jpg"
                            frame_path = event_frames_dir / frame_filename
                            cv2.imwrite(str(frame_path), frame)
                            frame_url = f"/event_frames/{frame_filename}"
                            logger.info(f"[FRAME SAVED] Frame saved: {frame_filename}")

                            # Extract detection list for easier access
                            detections_list = analysis.get('detections', [])
                            detected_objects = [d.get('label', '') for d in detections_list]

                            # Send analysis update (works without database) with frame
                            analysis_update = {
                                "camera_id": camera_id,
                                "scene_description": analysis.get('scene_description', ''),
                                "significance": significance,
                                "detections": detections_list,  # Full detection list
                                "detected_objects": detected_objects,  # List of object names
                                "detection_count": len(detections_list),
                                "context": context_summary,
                                "frame_url": frame_url,  # Always include frame URL
                                "frame_base64": frame_base64,  # Include base64 for direct display
                                "timestamp": datetime.utcnow().isoformat()
                            }
                            await manager.send_analysis_update(analysis_update)
                            logger.debug(f"[LIVE FEED] Updated (significance={significance}%)")

                            # Check for IMMEDIATE CRITICAL ALERTS - ANY EVENT CHANGE OR USER TASK >50%
                            scene_text = analysis.get('scene_description', '').lower()
                            activity_text = analysis.get('activity', '').lower()
                            combined_text = scene_text + ' ' + activity_text
                            
                            # Critical keywords for immediate alert (always trigger)
                            critical_keywords = ['weapon', 'gun', 'knife', 'violence', 'fight', 'attack', 
                                                'threat', 'dangerous', 'hazard', 'fire', 'smoke', 'blood',
                                                'injury', 'fall', 'accident', 'emergency', 'suspicious',
                                                'intruder', 'break', 'damage', 'vandal', 'unusual', 'anomaly']
                            
                            has_dangerous_keyword = any(keyword in combined_text for keyword in critical_keywords)
                            
                            # Check if user has active tasks
                            active_tasks = command_agent.get_active_tasks()
                            user_task_active = len(active_tasks) > 0 if active_tasks else False
                            
                            # IMMEDIATE ALERT TRIGGERS (User requirement: >=60% for critical events):
                            # 1. Dangerous keywords (always, any confidence)
                            # 2. User task match with >=60% accuracy
                            # 3. Critical events with >=60% significance
                            should_send_immediate = (
                                has_dangerous_keyword or  # Dangerous keywords (always)
                                (user_task_active and significance >= 60) or  # User task >=60%
                                (not user_task_active and significance >= 60)  # Critical event >=60%
                            )
                            
                            if should_send_immediate:
                                reason = []
                                if has_dangerous_keyword:
                                    reason.append("dangerous_keyword")
                                if user_task_active and significance >= 60:
                                    reason.append("user_task_match")
                                if significance >= 60:
                                    reason.append("critical_event")
                                
                                logger.info(f"🚨 IMMEDIATE CRITICAL ALERT: significance={significance}%, reasons={reason}")
                                # Determine alert type based on what triggered it
                                if has_dangerous_keyword:
                                    alert_type_text = "⚠️ HAZARDOUS/DANGEROUS EVENT"
                                    severity = "CRITICAL"
                                elif user_task_active:
                                    alert_type_text = "🎯 USER TASK DETECTED"
                                    severity = "CRITICAL"
                                else:
                                    alert_type_text = "🔔 EVENT CHANGE DETECTED"
                                    severity = "WARNING" if significance < 70 else "CRITICAL"
                                
                                alert_summary = f"""**🚨 IMMEDIATE ACTION REQUIRED** (Confidence: {significance}%)

**{alert_type_text}** - Requires immediate review!

**Scene:** {analysis.get('scene_description', 'No description')}

**Activity:** {analysis.get('activity', 'Unknown activity')}

**Objects Detected:** {', '.join(detected_objects) if detected_objects else 'None'}

**Detection Details:** {len(detections_list)} objects identified
**Time:** {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')}
**Camera:** {camera_id}
**Context:** {context_summary[:150] if context_summary else 'No context'}

**⚠️ ACTION REQUIRED:** Review this event immediately
**Evidence Attached:** Full image and detailed analysis included
**Alert Reason:** {'Dangerous activity' if has_dangerous_keyword else 'User task match' if user_task_active else 'Significant event change'}"""

                                title = f"🚨 IMMEDIATE ACTION REQUIRED - Camera {camera_id}"

                                # Send immediate alert
                                immediate_alert_data = {
                                    "id": f"immediate_{camera_id}_{int(datetime.utcnow().timestamp())}",
                                    "severity": severity,
                                    "title": title,
                                    "message": alert_summary,
                                    "camera_id": camera_id,
                                    "timestamp": datetime.utcnow().isoformat(),
                                    "significance": significance,
                                    "frame_url": frame_url,
                                    "frame_path": str(frame_path),
                                    "frame_base64": frame_base64,
                                    "detections": detections_list,
                                    "detected_objects": detected_objects,
                                    "alert_type": "immediate",
                                    "is_read": False
                                }

                                await manager.send_alert(immediate_alert_data)
                                logger.info(f"🚨 IMMEDIATE ALERT SENT: {severity} - {significance}% - {detected_objects}")

                            # Don't collect for 2-minute summary if already sent immediate alert
                            # This prevents duplicate notifications
                            # Only collect events that didn't trigger immediate alerts
                            elif not should_send_immediate and significance >= 50:
                                critical_events.append({
                                    'timestamp': current_time.isoformat(),
                                    'analysis': analysis,
                                    'significance': significance,
                                    'detected_objects': detected_objects,
                                    'detections_list': detections_list,
                                    'frame_url': frame_url,
                                    'frame_path': frame_path,
                                    'frame_base64': frame_base64,
                                    'context': context_summary
                                })
                                logger.info(f"✓ Event collected for 2-min summary (significance={significance}%)")

                            # Try to store event in database (optional - continue if fails)
                            try:
                                db = SessionLocal()
                                
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

                                # Create alert if significant (this is for DB storage, not WS notification)
                                if event.significance_score >= settings.WARNING_THRESHOLD:
                                    alert = Alert(
                                        event_id=event.id,
                                        severity=event.severity,
                                        title=f"{event.severity.value} Alert - Camera {camera_id}",
                                        message=event.scene_description
                                    )
                                    db.add(alert)
                                    db.flush()

                                db.commit()
                                db.close()
                            except Exception as db_error:
                                logger.warning(f"Failed to save event to database (continuing without DB): {db_error}")
                                try:
                                    if 'db' in locals():
                                        db.rollback()
                                        db.close()
                                except:
                                    pass
                        except Exception as frame_error:
                            logger.error(f"Error processing frame from camera {camera_id}: {frame_error}")
                            continue

                    # Check active tasks and analyze in context (for successfully processed frames)
                    if frame is not None:
                        try:
                            active_tasks = command_agent.get_active_tasks()
                            for task_id, task_data in active_tasks.items():
                                task_command = task_data.get('command', {})
                                task_params = task_command.get('parameters', {})
                                target_cameras = task_params.get('camera_ids', ['all'])

                                # Check if this camera is relevant to the task
                                if target_cameras == ['all'] or 'all' in target_cameras or camera_id in target_cameras:
                                    # Get analysis if we have it
                                    try:
                                        analysis = await vision_agent.analyze_frame(frame, camera_id)
                                        # Analyze in context of task
                                        task_result = await command_agent.analyze_with_context(
                                            task_id,
                                            {"camera_id": camera_id, "timestamp": datetime.utcnow().isoformat()},
                                analysis
                            )

                                        # Send task update if alert needed
                                        if task_result.get('alert_needed'):
                                            # Save frame for task alert
                                            timestamp_str = datetime.utcnow().strftime("%Y%m%d_%H%M%S_%f")
                                            frame_filename = f"camera{camera_id}_{timestamp_str}_task{task_id[-8:]}.jpg"
                                            frame_path = event_frames_dir / frame_filename
                                            cv2.imwrite(str(frame_path), frame)
                                            logger.info(f"[FRAME SAVED] Task alert triggered for task {task_id}, frame saved to: {frame_filename}")

                                            await manager.send_system_message("task_alert", {
                                                "task_id": task_id,
                                "camera_id": camera_id,
                                                "task_type": task_command.get('task_type'),
                                                "target": task_command.get('target'),
                                                "findings": task_result.get('findings'),
                                                "alert_message": task_result.get('alert_message'),
                                                "timestamp": datetime.utcnow().isoformat(),
                                                "frame_path": str(frame_path)  # Include frame path
                                            })
                                    except Exception as task_error:
                                        logger.debug(f"Task analysis error: {task_error}")
                        except Exception as task_check_error:
                            logger.debug(f"Error checking tasks: {task_check_error}")

            # Check if 2 minutes have elapsed - send summary alert
            if elapsed_seconds >= ANALYSIS_INTERVAL_SECONDS:
                logger.info(f"⏰ 2-MINUTE INTERVAL COMPLETE - Analyzing {len(critical_events)} events")
                
                if critical_events:
                    # Find most significant event
                    most_significant = max(critical_events, key=lambda x: x['significance'])
                    
                    # Collect all unique objects from the minute
                    all_objects = set()
                    activities = []
                    for event in critical_events:
                        all_objects.update(event['detected_objects'])
                        activity = event['analysis'].get('activity', '')
                        if activity and activity not in activities:
                            activities.append(activity)
                    
                    # Create comprehensive 2-minute summary
                    alert_summary = f"""**2-Minute Activity Summary** (Peak Confidence: {most_significant['significance']}%)

**Period:** {minute_start_time.strftime('%H:%M:%S')} - {current_time.strftime('%H:%M:%S')}

**Most Significant Scene:** {most_significant['analysis'].get('scene_description', 'No description')}

**Activities Detected:** {' → '.join(activities[:3]) if activities else 'No significant activity changes'}

**All Objects Seen:** {', '.join(sorted(all_objects)) if all_objects else 'None'}

**Events Recorded:** {len(critical_events)} detected in last 2 minutes
**Camera:** {camera_id if 'camera_id' in locals() else 0}

**Analysis:** This summary represents activities from the last 120 seconds."""

                    # Determine severity
                    if most_significant['significance'] >= 80:
                        severity = "CRITICAL"
                        title = f"🚨 Critical Activity Summary (2-min) - Camera {camera_id if 'camera_id' in locals() else 0}"
                    else:
                        severity = "WARNING"
                        title = f"⚠️ Activity Summary (2-min) - Camera {camera_id if 'camera_id' in locals() else 0}"

                    # Create ONE consolidated alert for the entire minute
                    alert_data = {
                        "id": f"summary_{int(current_time.timestamp())}",
                        "severity": severity,
                        "title": title,
                        "message": alert_summary,
                        "camera_id": camera_id if 'camera_id' in locals() else 0,
                        "timestamp": current_time.isoformat(),
                        "significance": most_significant['significance'],
                        "frame_url": most_significant['frame_url'],
                        "frame_path": str(most_significant['frame_path']),
                        "frame_base64": most_significant['frame_base64'],
                        "detections": most_significant['detections_list'],
                        "detected_objects": list(all_objects),
                        "event_count": len(critical_events),
                        "is_read": False
                    }

                    # Send single alert for entire 2-minute period
                    await manager.send_alert(alert_data)
                    logger.info(f"📩 2-MINUTE SUMMARY SENT: {severity} - {len(critical_events)} events, max={most_significant['significance']}%")
                else:
                    logger.info(f"✓ 2-minute period complete - No events to summarize")
                
                # Reset for next 2-minute period
                minute_start_time = current_time
                critical_events = []
                logger.info(f"🔄 Starting new 2-minute analysis period")

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
