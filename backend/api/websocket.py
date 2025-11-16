"""
WebSocket handlers for real-time communication
"""
from fastapi import WebSocket, WebSocketDisconnect
from typing import Dict, List, Set
import json
import asyncio
from datetime import datetime
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class ConnectionManager:
    """
    Manages WebSocket connections for real-time updates
    """

    def __init__(self):
        # Active connections by type
        self.active_connections: Dict[str, Set[WebSocket]] = {
            "live_feed": set(),
            "alerts": set(),
            "analysis": set(),
            "system": set()
        }

        # Connection metadata
        self.connection_info: Dict[WebSocket, Dict] = {}

    async def connect(self, websocket: WebSocket, connection_type: str = "system"):
        """
        Accept and register a new WebSocket connection

        Args:
            websocket: WebSocket connection
            connection_type: Type of connection (live_feed, alerts, analysis, system)
        """
        await websocket.accept()

        if connection_type not in self.active_connections:
            connection_type = "system"

        self.active_connections[connection_type].add(websocket)
        self.connection_info[websocket] = {
            "type": connection_type,
            "connected_at": datetime.utcnow(),
            "messages_sent": 0
        }

        # Send welcome message
        await self.send_personal_message({
            "type": "connection_established",
            "connection_type": connection_type,
            "timestamp": datetime.utcnow().isoformat(),
            "message": f"Connected to {connection_type} stream"
        }, websocket)

    def disconnect(self, websocket: WebSocket):
        """
        Remove a WebSocket connection

        Args:
            websocket: WebSocket connection to remove
        """
        # Remove from all connection sets
        for conn_set in self.active_connections.values():
            conn_set.discard(websocket)

        # Remove metadata
        if websocket in self.connection_info:
            del self.connection_info[websocket]

    async def send_personal_message(self, message: dict, websocket: WebSocket):
        """
        Send a message to a specific connection

        Args:
            message: Message dictionary
            websocket: Target WebSocket
        """
        try:
            await websocket.send_json(message)

            if websocket in self.connection_info:
                self.connection_info[websocket]["messages_sent"] += 1

        except Exception as e:
            print(f"Error sending message: {e}")
            self.disconnect(websocket)

    async def broadcast(self, message: dict, connection_type: str = None):
        """
        Broadcast message to all connections of a type

        Args:
            message: Message dictionary
            connection_type: Type of connections to broadcast to (None for all)
        """
        if connection_type and connection_type in self.active_connections:
            connections = self.active_connections[connection_type]
        else:
            # Broadcast to all
            connections = set()
            for conn_set in self.active_connections.values():
                connections.update(conn_set)

        # Send to all connections
        disconnected = []
        for connection in connections:
            try:
                await connection.send_json(message)

                if connection in self.connection_info:
                    self.connection_info[connection]["messages_sent"] += 1

            except Exception as e:
                print(f"Error broadcasting to connection: {e}")
                disconnected.append(connection)

        # Clean up disconnected
        for connection in disconnected:
            self.disconnect(connection)

    async def send_live_feed_update(self, camera_id: int, frame_data: str, analysis: dict):
        """
        Send live feed update to subscribed clients

        Args:
            camera_id: Camera ID
            frame_data: Base64 encoded frame
            analysis: Analysis results
        """
        message = {
            "type": "live_feed_update",
            "camera_id": camera_id,
            "timestamp": datetime.utcnow().isoformat(),
            "frame": frame_data,
            "analysis": analysis
        }

        await self.broadcast(message, "live_feed")

    async def send_alert(self, alert: dict):
        """
        Send alert notification

        Args:
            alert: Alert dictionary
        """
        message = {
            "type": "alert",
            "timestamp": datetime.utcnow().isoformat(),
            "alert": alert
        }

        await self.broadcast(message, "alerts")
        await self.broadcast(message, "system")  # Also send to system connections

    async def send_analysis_update(self, analysis: dict):
        """
        Send analysis update (scene narration)

        Args:
            analysis: Analysis results
        """
        message = {
            "type": "analysis_update",
            "timestamp": datetime.utcnow().isoformat(),
            "analysis": analysis
        }

        await self.broadcast(message, "analysis")

    async def send_system_message(self, message_type: str, data: dict):
        """
        Send system message

        Args:
            message_type: Type of system message
            data: Message data
        """
        message = {
            "type": message_type,
            "timestamp": datetime.utcnow().isoformat(),
            "data": data
        }

        await self.broadcast(message, "system")

    def get_connection_stats(self) -> dict:
        """
        Get connection statistics

        Returns:
            Statistics dictionary
        """
        stats = {
            "total_connections": sum(len(conns) for conns in self.active_connections.values()),
            "by_type": {
                conn_type: len(conns)
                for conn_type, conns in self.active_connections.items()
            },
            "active_connections": []
        }

        for websocket, info in self.connection_info.items():
            stats["active_connections"].append({
                "type": info["type"],
                "connected_at": info["connected_at"].isoformat(),
                "messages_sent": info["messages_sent"],
                "uptime_seconds": (datetime.utcnow() - info["connected_at"]).total_seconds()
            })

        return stats


# Global connection manager instance
manager = ConnectionManager()
