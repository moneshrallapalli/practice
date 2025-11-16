"""
Vision Agent - Handles Gemini Live API integration for real-time video analysis
"""
import google.generativeai as genai
from google.generativeai.types import GenerationConfig, HarmCategory, HarmBlockThreshold
import asyncio
import base64
import json
from datetime import datetime
from typing import Dict, Any, List, Optional, AsyncGenerator
import cv2
import numpy as np
from PIL import Image
import io
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import settings
from database.models import AlertSeverity


class VisionAgent:
    """
    Vision Agent for real-time video analysis using Gemini Live API
    """

    def __init__(self, api_key: str = None):
        """
        Initialize Vision Agent

        Args:
            api_key: Gemini API key
        """
        self.api_key = api_key or settings.GEMINI_API_KEY
        genai.configure(api_key=self.api_key)

        # Initialize Gemini model
        self.model = genai.GenerativeModel(
            model_name='gemini-1.5-flash-latest',  # Use flash for real-time processing
            generation_config=GenerationConfig(
                temperature=0.4,
                top_p=0.95,
                top_k=40,
                max_output_tokens=2048,
            ),
            safety_settings={
                HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_NONE,
                HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_NONE,
                HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_NONE,
                HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_NONE,
            }
        )

        # System prompt for surveillance analysis
        self.system_prompt = """You are an intelligent surveillance analysis system. Analyze the video stream continuously and provide:

1. OBJECT DETECTION: List all visible objects, people, vehicles with approximate locations
2. SCENE UNDERSTANDING: Describe the current scene and activity
3. CONTEXT AWARENESS: Note any changes from previous frames
4. SIGNIFICANCE: Rate the importance of current events (0-100)
5. NATURAL NARRATION: Provide a concise description of what's happening

Format your response as JSON with the following structure:
{
  "timestamp": "ISO timestamp",
  "scene_description": "Concise narrative description",
  "detections": [
    {
      "object_type": "person|vehicle|object|animal|other",
      "label": "specific description",
      "confidence": 0.95,
      "location": "approximate location in frame",
      "attributes": ["attribute1", "attribute2"]
    }
  ],
  "activity": "what is happening",
  "significance": 75,
  "changes": "what changed from previous frame",
  "alerts": [
    {
      "severity": "CRITICAL|WARNING|INFO",
      "message": "alert description"
    }
  ]
}

Focus on security-relevant events and anomalies. Be concise but thorough."""

    async def analyze_frame(
        self,
        frame: np.ndarray,
        camera_id: int,
        previous_context: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Analyze a single video frame using Gemini

        Args:
            frame: Video frame (numpy array)
            camera_id: Camera ID
            previous_context: Context from previous analysis

        Returns:
            Analysis results
        """
        try:
            # Convert frame to PIL Image
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            pil_image = Image.fromarray(frame_rgb)

            # Build prompt with context
            prompt = self.system_prompt
            if previous_context:
                prompt += f"\n\nPrevious context: {previous_context}"

            # Generate analysis
            response = await asyncio.to_thread(
                self.model.generate_content,
                [prompt, pil_image]
            )

            # Parse response
            analysis = self._parse_gemini_response(response.text)
            analysis['camera_id'] = camera_id
            analysis['timestamp'] = datetime.utcnow().isoformat()

            return analysis

        except Exception as e:
            return {
                "error": str(e),
                "camera_id": camera_id,
                "timestamp": datetime.utcnow().isoformat(),
                "scene_description": "Analysis failed",
                "significance": 0,
                "detections": [],
                "alerts": []
            }

    def _parse_gemini_response(self, response_text: str) -> Dict[str, Any]:
        """
        Parse Gemini's response into structured format

        Args:
            response_text: Raw response from Gemini

        Returns:
            Parsed analysis dictionary
        """
        try:
            # Try to extract JSON from response
            # Gemini might wrap JSON in markdown code blocks
            text = response_text.strip()

            # Remove markdown code block if present
            if text.startswith('```json'):
                text = text[7:]
            if text.startswith('```'):
                text = text[3:]
            if text.endswith('```'):
                text = text[:-3]

            text = text.strip()

            # Parse JSON
            analysis = json.loads(text)

            # Ensure required fields
            if 'scene_description' not in analysis:
                analysis['scene_description'] = text[:200]
            if 'significance' not in analysis:
                analysis['significance'] = 50
            if 'detections' not in analysis:
                analysis['detections'] = []
            if 'alerts' not in analysis:
                analysis['alerts'] = []

            return analysis

        except json.JSONDecodeError:
            # If JSON parsing fails, create structured response from text
            return {
                "scene_description": response_text[:500],
                "significance": 50,
                "detections": [],
                "activity": response_text[:200],
                "changes": "",
                "alerts": []
            }

    async def analyze_stream(
        self,
        camera_id: int,
        video_source: Any,
        fps: int = 2
    ) -> AsyncGenerator[Dict[str, Any], None]:
        """
        Continuously analyze video stream

        Args:
            camera_id: Camera ID
            video_source: Video source (file path, URL, or camera index)
            fps: Frames per second to analyze

        Yields:
            Analysis results for each frame
        """
        cap = cv2.VideoCapture(video_source)
        frame_interval = 1.0 / fps
        previous_context = None

        try:
            while cap.isOpened():
                ret, frame = cap.read()
                if not ret:
                    break

                # Analyze frame
                analysis = await self.analyze_frame(frame, camera_id, previous_context)

                # Update context for next frame
                previous_context = analysis.get('scene_description', '')[:200]

                yield analysis

                # Wait for next frame
                await asyncio.sleep(frame_interval)

        finally:
            cap.release()

    def calculate_significance_score(self, analysis: Dict[str, Any]) -> int:
        """
        Calculate significance score for an event

        Args:
            analysis: Analysis results

        Returns:
            Significance score (0-100)
        """
        base_score = analysis.get('significance', 50)

        # Boost score based on detections
        detections = analysis.get('detections', [])
        detection_boost = min(len(detections) * 5, 20)

        # Boost score based on alerts
        alerts = analysis.get('alerts', [])
        alert_boost = 0
        for alert in alerts:
            if alert.get('severity') == 'CRITICAL':
                alert_boost += 30
            elif alert.get('severity') == 'WARNING':
                alert_boost += 15
            elif alert.get('severity') == 'INFO':
                alert_boost += 5

        total_score = min(base_score + detection_boost + alert_boost, 100)
        return total_score

    def determine_alert_severity(self, analysis: Dict[str, Any]) -> AlertSeverity:
        """
        Determine alert severity based on analysis

        Args:
            analysis: Analysis results

        Returns:
            Alert severity
        """
        significance = self.calculate_significance_score(analysis)
        alerts = analysis.get('alerts', [])

        # Check for critical alerts
        for alert in alerts:
            if alert.get('severity') == 'CRITICAL':
                return AlertSeverity.CRITICAL

        # Check significance thresholds
        if significance >= settings.CRITICAL_THRESHOLD:
            return AlertSeverity.CRITICAL
        elif significance >= settings.WARNING_THRESHOLD:
            return AlertSeverity.WARNING
        else:
            return AlertSeverity.INFO

    async def batch_analyze_frames(
        self,
        frames: List[np.ndarray],
        camera_id: int
    ) -> List[Dict[str, Any]]:
        """
        Analyze multiple frames in batch

        Args:
            frames: List of video frames
            camera_id: Camera ID

        Returns:
            List of analysis results
        """
        tasks = [self.analyze_frame(frame, camera_id) for frame in frames]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Filter out exceptions
        valid_results = []
        for result in results:
            if isinstance(result, dict):
                valid_results.append(result)
            else:
                valid_results.append({
                    "error": str(result),
                    "camera_id": camera_id,
                    "timestamp": datetime.utcnow().isoformat(),
                    "scene_description": "Analysis failed",
                    "significance": 0,
                    "detections": [],
                    "alerts": []
                })

        return valid_results

    def extract_detections_for_storage(
        self,
        analysis: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """
        Extract detections in format suitable for database storage

        Args:
            analysis: Analysis results

        Returns:
            List of detection dictionaries
        """
        detections = []
        for det in analysis.get('detections', []):
            detections.append({
                "object_type": det.get('object_type', 'unknown'),
                "object_label": det.get('label', ''),
                "confidence_score": det.get('confidence', 0.0),
                "bounding_box": det.get('bounding_box', {}),
                "attributes": det.get('attributes', []),
                "location": det.get('location', '')
            })

        return detections
